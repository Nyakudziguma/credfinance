import random
from .models import Sessions
from chat.models import Client
from .utils import *
from .messageFunctions import *
from .chat import faq_message
from django.shortcuts import get_object_or_404
import time
from chat.views import handle_client_message

def WhatsappChatHandling(fromId, message, profileName, phoneId, text, image, selected_id, data, document, button, reply_data):
    try:
        chat = Sessions.objects.get(user__phone_number=fromId)
        conversation = Conversation.objects.filter(
                user=chat.user, 
                start_time__gte=now() - timedelta(hours=24)
            ).first()

        if not conversation:
            conversation = Conversation.objects.create(user=chat.user)
    except Sessions.DoesNotExist:
        try:
            user = Client.objects.get(phone_number=fromId)
        except Client.DoesNotExist:
            user = Client.objects.create(
                phone_number=fromId,
                name=fromId,              
            )
        try:
            chat = Sessions.objects.get(user=user)
            conversation = Conversation.objects.create(user=chat.user)
        except Sessions.DoesNotExist:
            chat = Sessions.objects.create(user=user)
            conversation = Conversation.objects.create(user=chat.user)

        
    menu_list = ['hi', 'hy', 'hey', 'hie', 'hello', 'menu', 'reply']

    if text and text.lower() in menu_list or selected_id and selected_id.lower() in menu_list:
        chat.state ='menu'
        chat.position='menu'
        chat.save()
        message = "Hello, I'm Tasha, your WhatsApp assistant. Please select an option."
        return MainMenu(fromId, message)
    
    elif chat.state =='menu' and chat.state =='menu':

        if selected_id =='faqs':
            chat.state ='faqs'
            chat.position='faqs'
            chat.save()
            message = 'Please type your query so I can assist you'
            return sendWhatsAppMessage(fromId, message)
        
        elif selected_id =='live_chat' or text =='2':
            chat.state ='live_chat'
            chat.position = 'live_chat'
            chat.save()
           
            message = 'Please type your query and send so I can connect you to an agent'
            return sendWhatsAppMessage(fromId,message)
        
        else:
            message = 'Please select an option from the menu'
            return MainMenu(fromId, message)
    
    elif chat.state =='faqs' and chat.position=='faqs':
        message = faq_message(text)
        return sendWhatsAppMessage(fromId, message)
    
    elif chat.state =='live_chat' and chat.position=='live_chat':
        return handle_client_message(fromId, text)
    