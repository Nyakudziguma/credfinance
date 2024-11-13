import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatRoom, Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        sender_type = data['sender_type']
        sender_id = data['sender_id']

        # Save message to the database
        chatroom = await self.get_chatroom(self.room_name)
        await self.save_message(chatroom, sender_type, sender_id, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_type': sender_type,
                'sender_id': sender_id
            }
        )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_type': event['sender_type'],
            'sender_id': event['sender_id']
        }))

    @staticmethod
    async def get_chatroom(room_name):
        return await ChatRoom.objects.async_get(id=room_name)

    @staticmethod
    async def save_message(chatroom, sender_type, sender_id, content):
        await Message.objects.async_create(
            chatroom=chatroom,
            sender_type=sender_type,
            sender_id=sender_id,
            content=content
        )
