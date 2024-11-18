import json
from channels.generic.websocket import WebsocketConsumer
from .models import ChatRoom, Message, Client, Account
from channels.exceptions import StopConsumer
from django.shortcuts import get_object_or_404,redirect

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        # self.user = self.scope['user']
        # self.chatroom_id = self.scope['url_route']['kwargs']['chatroom_id']
        # self.chatroom = get_object_or_404(ChatRoom, id=self.chatroom_id)
        self.accept()

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        content = text_data_json.get('content', '')
        sender_type = text_data_json.get('sender_type', '')
        sender_name = text_data_json.get('sender_name', '')

        if sender_type == 'agent':
            sender = Account.objects.get(phone_number=sender_name)
        elif sender_type == 'client':
            sender = Client.objects.get(name=sender_name)
            
        message = Message.objects.create(
            chatroom=self.chatroom,
            content=content,
            sender_type=sender_type,
            sender=sender
        )