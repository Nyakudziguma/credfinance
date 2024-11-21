# routing.py
from django.urls import re_path
from chat.consumers import *

websocket_urlpatterns = [
     re_path(r'wss/chat/(?P<chatroom_id>\d+)/$', ChatConsumer.as_asgi()),
     re_path(r'wss/list/$', ChatListConsumer.as_asgi()),
     re_path(r'wss/dashboard_stats/$', DashboardStatsConsumer.as_asgi()),

]