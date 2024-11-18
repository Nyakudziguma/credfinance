from django.urls import path
from . import views
urlpatterns = [
     # path('<str:room_name/>',views.room, name='reset-password'),
      path('chats', views.chats, name = 'chats'),
      path('chats/<int:chatroom_id>/', views.chats, name='chatroom'),  # Specific chatroom
       path('send_message/<int:chatroom_id>/', views.send_message, name='send_message'),

]