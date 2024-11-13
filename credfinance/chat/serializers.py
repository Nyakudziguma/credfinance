from rest_framework import serializers
from .models import Client, ChatRoom, Message

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'client_id', 'name', 'contact_info']

class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = ['id', 'agent', 'client', 'created_at', 'updated_at']

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'chatroom', 'sender_type', 'sender_id', 'content', 'timestamp', 'is_read']
