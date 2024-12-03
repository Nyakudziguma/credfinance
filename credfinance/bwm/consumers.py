
import json
from channels.generic.websocket import WebsocketConsumer
from channels.exceptions import StopConsumer
from .models import MessageResponse, BulkMessages
from rest_framework.permissions import AllowAny
from django.template.loader import render_to_string
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

class BWMStatsConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope.get('user', None)
        if user and user.is_authenticated:
            await self.channel_layer.group_add("bulk_messaging_stats", self.channel_name)
            await self.accept()

            # Send the initial chatroom count
            total_messages = await self.get_total_messages_count()
            failed_messages = await self.get_failed_messages_count()
            successful_messages = await self.get_successful_messages()

            await self.send_json({
                'type': 'bulk_messages_count',
                'total_messages': total_messages,
                'failed_messages': failed_messages,
                'successful_messages': successful_messages,
            })
        else:
            print("User is not authenticated")
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("bulk_messaging_stats", self.channel_name)

    async def chatroom_count_update(self, event):
        await self.send_json({
            'type': 'bulk_messages_count',
            'total_messages': event['total_messages'],
            'failed_messages':event['failed_messages'],
            'successful_messages':event['successful_messages'],
        })

    async def get_total_messages_count(self):
        return await database_sync_to_async(MessageResponse.objects.count)()
    
    async def get_failed_messages_count(self):
        return await database_sync_to_async(lambda: MessageResponse.objects.filter(status='Failed').count())()

    async def get_successful_messages(self):
        return await database_sync_to_async(lambda: MessageResponse.objects.filter(status='Successful').count())()

