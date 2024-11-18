import json
from channels.generic.websocket import WebsocketConsumer
from channels.exceptions import StopConsumer
from .models import ChatRoom, Message, Client, Account
from rest_framework.permissions import AllowAny
from django.template.loader import render_to_string

class ChatConsumer(WebsocketConsumer):
    permission_classes = [AllowAny]
    
    def connect(self):
        try:
            user = self.scope.get('user', None)  # Get the authenticated user
            if user and user.is_authenticated:
                self.chatroom_id = self.scope['url_route']['kwargs']['chatroom_id']
                print(f"Connecting user {user} to chatroom ID: {self.chatroom_id}")

                self.chatroom = self.get_chatroom(self.chatroom_id)
                if not self.chatroom:
                    print(f"Chatroom ID {self.chatroom_id} not found")
                    self.close()
                    raise StopConsumer()

                self.room_group_name = f'chat_{self.chatroom.id}'
                self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
                self.accept()

                messages = self.get_messages(self.chatroom)
                messages_data = self.format_messages(messages)

                # Send initial chat history to the user
                self.send(text_data=json.dumps({'messages': messages_data}))
                print(f"Connection accepted for chatroom {self.chatroom_id}")
            else:
                print("User is not authenticated")
                self.close()
                raise StopConsumer()
        except Exception as e:
            print(f"Error in connect: {e}")
            self.close()
            raise StopConsumer()

    def disconnect(self, close_code):
        try:
            if hasattr(self, 'room_group_name'):
                self.channel_layer.group_discard(
                    self.room_group_name,
                    self.channel_name
                )
        except Exception as e:
            print(f"Error in disconnect: {e}")
        finally:
            raise StopConsumer()

    def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            content = text_data_json.get('content', '')
            sender_type = text_data_json.get('sender_type', '')
            sender_name = text_data_json.get('sender_name', '')

            # Create and format the new message
            message = self.create_message(self.chatroom, content, sender_type, sender_name)
            message_data = self.format_message(message)

            # Broadcast the message to the group
            self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message_data
                }
            )
        except Exception as e:
            self.send(text_data=json.dumps({'error': str(e)}))
            print(f"Error in receive: {e}")

    def chat_message(self, event):
        # Send message to WebSocket
        message = event['message']
        self.send(text_data=json.dumps({'message': message}))

    # Helper methods
    def get_chatroom(self, chatroom_id):
        try:
            return ChatRoom.objects.get(id=chatroom_id)
        except ChatRoom.DoesNotExist:
            return None

    def get_messages(self, chatroom):
        return list(Message.objects.filter(chatroom=chatroom).order_by('timestamp'))

    def format_message(self, message):
        return {
            'sender_name': message.sender.phone_number if hasattr(message.sender, 'phone_number') else message.sender.name,
            'sender_type': message.sender_type,
            'content': message.content,
            'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        }

    def format_messages(self, messages):
        return [
            {
                'sender_name': message.sender.phone_number if hasattr(message.sender, 'phone_number') else message.sender.name,
                'sender_type': message.sender_type,
                'content': message.content,
                'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            }
            for message in messages
        ]

    def create_message(self, chatroom, content, sender_type, sender_name):
        try:
            if sender_type == 'agent':
                sender = Account.objects.get(phone_number=sender_name)
            elif sender_type == 'client':
                sender = Client.objects.get(name=sender_name)
            else:
                raise ValueError("Invalid sender type")

            return Message.objects.create(
                chatroom=chatroom,
                content=content,
                sender_type=sender_type,
                sender=sender
            )
        except Account.DoesNotExist:
            raise ValueError(f"Account with phone number {sender_name} not found")
        except Client.DoesNotExist:
            raise ValueError(f"Client with name {sender_name} not found")


class ChatroomListConsumer(WebsocketConsumer):
    permission_classes = [AllowAny]
    
    def connect(self):
        try:
            user = self.scope.get('user', None)
            if user and user.is_authenticated:
                print(f"Connecting user {user} to chatroom list websocket")

                self.room_group_name = 'chatroom_list'
                self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
                self.accept()

                # Send initial chatroom list
                chatrooms = self.get_chatrooms()
                html_content = self.render_chatroom_list(chatrooms)
                self.send(text_data=json.dumps({
                    'type': 'chatroom_list_update',
                    'html': html_content
                }))
                print("Chatroom list connection accepted")
            else:
                print("User is not authenticated")
                self.close()
                raise StopConsumer()
        except Exception as e:
            print(f"Error in connect: {e}")
            self.close()
            raise StopConsumer()

    def disconnect(self, close_code):
        try:
            if hasattr(self, 'room_group_name'):
                self.channel_layer.group_discard(
                    self.room_group_name,
                    self.channel_name
                )
        except Exception as e:
            print(f"Error in disconnect: {e}")
        finally:
            raise StopConsumer()

    def receive(self, text_data):
        try:
            # Handle any direct messages to this consumer
            text_data_json = json.loads(text_data)
            if text_data_json.get('type') == 'request_update':
                chatrooms = self.get_chatrooms()
                html_content = self.render_chatroom_list(chatrooms)
                self.send(text_data=json.dumps({
                    'type': 'chatroom_list_update',
                    'html': html_content
                }))
        except Exception as e:
            self.send(text_data=json.dumps({'error': str(e)}))
            print(f"Error in receive: {e}")

    def chatroom_list_update(self, event):
        # Broadcast the updated list to all connected clients
        self.send(text_data=json.dumps({
            'type': 'chatroom_list_update',
            'html': event['html']
        }))

    # Helper methods
    def get_chatrooms(self):
        return ChatRoom.objects.all().order_by('-latest_message__timestamp')

    def render_chatroom_list(self, chatrooms):
        return render_to_string('apps/chatroom_list.html', {
            'chatrooms': chatrooms
        })