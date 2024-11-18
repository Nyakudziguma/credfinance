from django.contrib import admin
from .models import Client, ChatRoom, Message

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = [i.name for i in Client._meta.fields]
    search_fields = ('id', 'name', 'phone_number')

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = [i.name for i in ChatRoom._meta.fields]
    search_fields = ('agent__username', 'client__name')
    list_filter = ('created_at', 'updated_at')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = [i.name for i in Message._meta.fields]
    list_filter = ('timestamp', 'is_read', 'sender_type')
    search_fields = ('content',)
    ordering = ('-timestamp',)

    def sender_name(self, obj):
        sender = obj.sender
        return sender.username if obj.sender_type == 'agent' else sender.name
    sender_name.short_description = 'Sender'
