import json
from channels.db import database_sync_to_async

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .models import CompanyBalance

class BalanceStatsConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope.get('user', None)
        if user and user.is_authenticated:
            await self.channel_layer.group_add("balance_stats", self.channel_name)
            await self.accept()

            user_balance = await self.get_user_balances(user.company)

            await self.send_json({
                'type': 'user_balance',
                'user_balance': user_balance,
            })
        else:
            print("User is not authenticated")
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("balance_stats", self.channel_name)

    async def company_balance_update(self, event):
        await self.send_json({
            'type': 'user_balance',
            'user_balance': event['company_balance'],  # Use the event data
        })

    async def get_user_balances(self, company):
        try:
            balance = await database_sync_to_async(lambda: CompanyBalance.objects.get(company=company))()
            return str(balance.balance)  # Convert Decimal to string
        except CompanyBalance.DoesNotExist:
            return "0"
