from django.contrib import admin
from .models import Client, ChatRoom, Message

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('client_id', 'name', 'contact_info')
    search_fields = ('client_id', 'name')

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'agent', 'client', 'created_at', 'updated_at')
    search_fields = ('agent__username', 'client__name')
    list_filter = ('created_at', 'updated_at')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chatroom', 'sender_type', 'content', 'timestamp', 'is_read')
    list_filter = ('timestamp', 'is_read', 'sender_type')
    search_fields = ('content',)
    ordering = ('-timestamp',)

    def sender_name(self, obj):
        sender = obj.sender
        return sender.username if obj.sender_type == 'agent' else sender.name
    sender_name.short_description = 'Sender'
