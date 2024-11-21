import json
from channels.generic.websocket import WebsocketConsumer
from channels.exceptions import StopConsumer
from .models import ChatRoom, Message, Client, Account
from rest_framework.permissions import AllowAny
from django.template.loader import render_to_string
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.serializers import serialize
from django.utils import timezone
from django.db.models import Max
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncJsonWebsocketConsumer


class ChatConsumer(WebsocketConsumer):
    permission_classes = [AllowAny]

    def connect(self):
        try:
            user = self.scope.get('user', None)
            if not user or not user.is_authenticated:
                self.close()
                return

            self.chatroom_id = self.scope['url_route']['kwargs']['chatroom_id']
            self.chatroom = self.get_chatroom(self.chatroom_id)
            if not self.chatroom:
                self.close()
                return

            self.setup_groups()
            self.accept()
            self.send_initial_messages()
            
        except Exception:
            self.close()

    def setup_groups(self):
        self.room_group_name = f'chat_{self.chatroom.id}'
        self.message_group_name = f'message_{self.chatroom.id}'
        
        for group_name in [self.room_group_name, self.message_group_name]:
            async_to_sync(self.channel_layer.group_add)(
                group_name,
                self.channel_name
            )

    def send_initial_messages(self):
        messages = self.get_messages(self.chatroom)
        messages_data = self.format_messages(messages)
        self.send(text_data=json.dumps({'messages': messages_data}))

    def disconnect(self, close_code):
        for group_name in ['room_group_name', 'message_group_name']:
            if hasattr(self, group_name):
                async_to_sync(self.channel_layer.group_discard)(
                    getattr(self, group_name),
                    self.channel_name
                )

    def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = self.process_message(data)
            
            # Send only one broadcast
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': self.format_message(message)
                }
            )
        except Exception as e:
            self.send(text_data=json.dumps({'error': str(e)}))

    def chat_message(self, event):
        message = event['message']
        html_message = self.format_message_as_html(message)
        self.send(text_data=json.dumps({
            'html': html_message,
            'message': message
        }))

    def process_message(self, data):
        content = data.get('content', '')
        sender_type = data.get('sender_type', '')
        sender_name = data.get('sender_name', '')
        
        message = self.create_message(self.chatroom, content, sender_type, sender_name)
        return self.format_message(message)

    def broadcast_message(self, message_data):
        broadcasts = [
            (self.room_group_name, {
                'type': 'chat_message',
                'message': message_data
            }),
            (self.message_group_name, {
                'type': 'chat_update',
                'chatroom_id': self.chatroom.id,
                'content': message_data['content'],
                'timestamp': message_data['timestamp'],
                'sender_type': message_data['sender_type'],
                'sender_name': message_data['sender_name']
            }),
            ('sidebar_updates', {
                'type': 'sidebar_update',
                'chatroom_id': self.chatroom.id,
                'latest_message': message_data
            })
        ]

        for group_name, message in broadcasts:
            async_to_sync(self.channel_layer.group_send)(group_name, message)

    def chat_update(self, event):
        messages = self.get_chatroom_messages()
        self.send(text_data=json.dumps({
            'type': 'message_update',
            'chatrooms': messages,
            'chatroom_id': event['chatroom_id'],
            'content': event['content'],
            'timestamp': event['timestamp'],
            'sender_type': event['sender_type'],
            'sender_name': event['sender_name']
        }))

    def sidebar_update(self, event):
        self.send(text_data=json.dumps({
            'chatroom_id': event['chatroom_id'], 
            'latest_message': event['latest_message']
        }))

    # Helper methods
    def format_message_as_html(self, message):
        return render_to_string('apps/chat_message.html', {'message': message})

    def get_chatroom(self, chatroom_id):
        try:
            return ChatRoom.objects.get(id=chatroom_id)
        except ChatRoom.DoesNotExist:
            return None

    def get_messages(self, chatroom):
        return Message.objects.filter(chatroom=chatroom).order_by('timestamp')

    def get_chatroom_messages(self):
        return Message.objects.filter(chatroom=self.chatroom).order_by('timestamp')

    def format_message(self, message):
        return {
            'sender_name': message.sender.name if hasattr(message.sender, 'name') else message.sender.phone_number,
            'sender_type': message.sender_type,
            'content': message.content,
            'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        }

    def format_messages(self, messages):
        return [self.format_message(message) for message in messages]

    def create_message(self, chatroom, content, sender_type, sender_name):
        sender_model = Account if sender_type == 'agent' else Client
        lookup_field = 'phone_number' if sender_type == 'agent' else 'name'
        
        sender = sender_model.objects.get(**{lookup_field: sender_name})
        return Message.objects.create(
            chatroom=chatroom,
            content=content,
            sender_type=sender_type,
            sender_id=sender.id
        )


class ChatListConsumer(WebsocketConsumer):
    permission_classes = [AllowAny]

    def connect(self):
        try:
            user = self.scope.get('user', None)
            if user and user.is_authenticated:
                print(f"Connecting user {user} to lists")
                self.accept()
            
                # Join chat_updates group
                async_to_sync(self.channel_layer.group_add)(
                    "chat_updates",
                    self.channel_name
                )
            else:
                print("User is not authenticated")
                self.close()
                raise StopConsumer()
        except Exception as e:
            print(f"Error in connect: {e}")
            self.close()
            raise StopConsumer()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            "chat_updates",
            self.channel_name
        )

    def chat_update(self, event):
        try:
            # Get updated chatroom list
            print("updating room")
            chatrooms = self.get_chatroom_list()
            
            self.send(text_data=json.dumps({
                'type': 'chat_update',
                'chatrooms': chatrooms,
                'chatroom_id': event['chatroom_id'],
                'message_content': event['message_content'],
                'timestamp': event['timestamp'],
                'sender_name': event['sender_name']
            }))
        except Exception as e:
            print(f"Error in chat_update: {e}")

    def get_chatroom_list(self):
        chatrooms = ChatRoom.objects.all().annotate(
            latest_message_timestamp=Max('messages__timestamp')
        ).order_by('-latest_message_timestamp')
        
        chatroom_list = []
        for chatroom in chatrooms:
            latest_message = Message.objects.filter(chatroom=chatroom).order_by('-timestamp').first()
            chatroom_list.append({
                'id': chatroom.id,
                'client_name': chatroom.client.name,
                'latest_message': latest_message.content if latest_message else 'No messages yet',
                'timestamp': latest_message.timestamp.strftime('%Y-%m-%d %H:%M:%S') if latest_message else chatroom.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        return chatroom_list
    

class DashboardStatsConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope.get('user', None)
        if user and user.is_authenticated:
            await self.channel_layer.group_add("dashboard_stats", self.channel_name)
            await self.accept()

            # Send the initial chatroom count
            total_chatrooms = await self.get_chatroom_count()
            total_messages = await self.get_messages_count()
            unread_messages = await self.get_unread_messages()
            read_messages = await self.get_read_messages()

            await self.send_json({
                'type': 'chatroom_count',
                'total_chatrooms': total_chatrooms,
                'total_messages': total_messages,
                'unread_messages': unread_messages,
                'read_messages': read_messages,
            })
        else:
            print("User is not authenticated")
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("dashboard_stats", self.channel_name)

    async def chatroom_count_update(self, event):
        await self.send_json({
            'type': 'chatroom_count',
            'total_chatrooms': event['total_chatrooms'],
            'total_messages': event['total_messages'],
            'unread_messages':event['unread_messages'],
            'read_messages':event['unread_messages'],
        })

    async def get_chatroom_count(self):
        return await database_sync_to_async(ChatRoom.objects.count)()
    
    async def get_messages_count(self):
        return await database_sync_to_async(Message.objects.count)()
    
    async def get_unread_messages(self):
        return await database_sync_to_async(lambda: Message.objects.filter(is_read=False).count())()

    async def get_read_messages(self):
        return await database_sync_to_async(lambda: Message.objects.filter(is_read=True).count())()

