# routing.py
from django.urls import re_path
from chat.consumers import ChatConsumer, ChatListConsumer, DashboardStatsConsumer
from bwm.consumers import BWMStatsConsumer
from balances.consumers import BalanceStatsConsumer

websocket_urlpatterns = [
     re_path(r'wss/chat/(?P<chatroom_id>\d+)/$', ChatConsumer.as_asgi()),
     re_path(r'wss/list/$', ChatListConsumer.as_asgi()),
     re_path(r'wss/dashboard_stats/$', DashboardStatsConsumer.as_asgi()),
     
     re_path(r'wss/bulk_messaging_stats/$', BWMStatsConsumer.as_asgi()),
     re_path(r'wss/balance_stats/$', BalanceStatsConsumer.as_asgi()),

]