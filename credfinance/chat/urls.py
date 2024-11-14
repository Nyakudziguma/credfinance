from django.urls import path
from . import views
urlpatterns = [
     # path('<str:room_name/>',views.room, name='reset-password'),
      path('chats', views.chats, name = 'chats'),
]