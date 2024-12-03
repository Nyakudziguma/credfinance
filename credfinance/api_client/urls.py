from django.urls import path
from .views import HandleClientMessageView

urlpatterns = [
      path('handle-chat-messages/', HandleClientMessageView.as_view(), name = 'api_handle_client_message'),
      
]