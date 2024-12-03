import json
from .models import Client, ChatRoom, Message
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404,redirect
from django.db.models import Max
from django.views.decorators.csrf import csrf_exempt
from accounts.models import Account, CompanyAuthentication
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.template.loader import render_to_string
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from bot.messageFunctions import sendWhatsAppMessage
from balances.models import CompanyBalance
import requests
from django.http import JsonResponse
from django.urls import reverse

def handle_client_message(phone_number, message_content):
    """
    Handles incoming messages from clients via WhatsApp.
    """
    try:
        try:
            client = Client.objects.get(phone_number=phone_number)
            company = client.company
        except Client.DoesNotExist:
            client = Client.objects.create(
                phone_number=phone_number,
                name=phone_number  
            )
    
        chatroom, created = ChatRoom.objects.get_or_create(client=client, status='open')
        
        content = message_content

        message = Message.objects.create(
            chatroom=chatroom,
            content=content,
            sender_type='client',
            sender_id=client.id
        )

        chatroom.latest_message = message
        chatroom.save()

        local_time = timezone.localtime(message.timestamp)
        formatted_timestamp = local_time.strftime('%Y-%m-%d %H:%M:%S')

        message_context = {
            'message': {
                'sender': client,
                'content': content,
                'sender_type': 'client',
                'timestamp': formatted_timestamp
            }
        }

        html_message = render_to_string('apps/chat_message.html', message_context)

        channel_layer = get_channel_layer()
        
        async_to_sync(channel_layer.group_send)(
            f"chat_{chatroom.id}",
            {
                "type": "chat_message",
                "html": html_message,
                "message": {
                    'sender_name': client.name,
                    'sender_type': 'client',
                    'content': content,
                    'timestamp': formatted_timestamp,
                }
            }
        )

        async_to_sync(channel_layer.group_send)(
            "chat_updates",
            {
                "type": "chat_update",
                "chatroom_id": chatroom.id,
                "message_content": content,
                "timestamp": formatted_timestamp,
                "sender_name": client.name,
                "is_read": message.is_read,
            }
        )
        
        total_chatrooms = ChatRoom.objects.count()
        total_messages = Message.objects.count()
        unread_messages = Message.objects.filter(is_read=False).count()
        read_messages = Message.objects.filter(is_read=True).count()
        total_users = Client.objects.filter(company=company).count()
        company_balance = CompanyBalance.objects.get(company=company)
        balance = str(company_balance.balance)

        async_to_sync(channel_layer.group_send)(
            "dashboard_stats",
            {
                "type": "chatroom_count_update",
                "total_chatrooms": total_chatrooms,
                "total_messages": total_messages,
                'unread_messages': unread_messages,
                'read_messages': read_messages,
                'total_users': total_users,
                'company_balance': balance,
            }
        )
       

        return {
            "success": True,
            "chatroom_id": chatroom.id,
            "message_id": message.id,
            "html": html_message
        }
        
    except Exception as e:
        print(f"Error in send_message: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@login_required
def send_message(request, chatroom_id):
    if request.method == 'POST':
        try:
            chatroom = ChatRoom.objects.get(id=chatroom_id)
            content = request.POST.get('content', '').strip()
            image = request.FILES.get('image', None)

            if not content:
                return HttpResponse('')
            
            sender = Account.objects.get(id=request.user.id)
            message = Message.objects.create(
                chatroom=chatroom,
                content=content,
                sender_type='agent',
                sender_id=sender.id,
                image=image if image else None,
            )

            chatroom.latest_message = message
            chatroom.save()

            message_context = {
                'message': message,
                'sender_name': sender.first_name,
                'timestamp': timezone.localtime(message.timestamp).strftime('%Y-%m-%d %H:%M:%S'),
            }

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"chat_{chatroom_id}",
                {
                    "type": "chat_message",
                    "message": {
                        'sender_name': sender.first_name,
                        'sender_type': 'agent',
                        'content': content,
                        "image_url": message.image.url if message.image else None,
                        'timestamp': message_context['timestamp'],
                    }
                }
            )
            async_to_sync(channel_layer.group_send)(
                "chat_updates",
                {
                    "type": "chat_update",
                    "chatroom_id": chatroom.id,
                    "message_content": content,
                    "timestamp": message_context['timestamp'],
                    "sender_name": sender.first_name,
                    "is_read": message.is_read,
                }
            )
            total_chatrooms = ChatRoom.objects.count()
            total_messages = Message.objects.count()
            unread_messages = Message.objects.filter(is_read=False).count()
            read_messages = Message.objects.filter(is_read=True).count()
            total_users = Client.objects.filter(company=request.user.company).count()
            company_balance = CompanyBalance.objects.get(company=request.user.company)
            balance = str(company_balance.balance)

            async_to_sync(channel_layer.group_send)(
                "dashboard_stats",
                {
                    "type": "chatroom_count_update",
                    "total_chatrooms": total_chatrooms,
                    "total_messages": total_messages,
                    'unread_messages': unread_messages,
                    'read_messages': read_messages,
                    'total_users': total_users,
                    'company_balance': balance,
                }
            )
            
            try:
                company = CompanyAuthentication.objects.get(company=request.user.company)
                token = company.meta_token
                meta_url = company.meta_url
                sendWhatsAppMessage(chatroom.client.phone_number, content, token, meta_url)
            except Exception as e:
                print(e)

            return HttpResponse('')  
            
        except Exception as e:
            print(e)
            return HttpResponse(status=500)
            
    return HttpResponse(status=400)

@login_required
def chats(request, chatroom_id=None):
    chatrooms = ChatRoom.objects.annotate(
        latest_message_timestamp=Max('messages__timestamp')
    ).order_by('-latest_message_timestamp')  
    for chatroom in chatrooms:
        chatroom.latest_message = Message.objects.filter(chatroom=chatroom).order_by('-timestamp').first()

    if chatroom_id:
        chatroom = get_object_or_404(ChatRoom, id=chatroom_id)
        messages = Message.objects.filter(chatroom=chatroom).order_by('timestamp')
        for message in messages:
            message.is_read = True
            message.save()
    else:
        chatroom = None
        messages = []

    return render(request, 'apps/chat.html', {
        'chatrooms': chatrooms,
        'chatroom': chatroom,
        'messages': messages
    })



@login_required
def create_message(request, chatroom_id):
    if request.method == 'POST':
        content = request.POST.get('content')
        chatroom = get_object_or_404(ChatRoom, id=chatroom_id)
        message = Message.objects.create(
            chatroom=chatroom,
            content=content,
            sender=request.user
        )

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "chat_updates",
            {
                "type": "chat_update",
                "chatroom_id": chatroom.id,
                "message_content": content,
                "timestamp": message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                "sender_name": request.user.get_full_name() or request.user.username
            }
        )

        async_to_sync(channel_layer.group_send)(
            f"message_{chatroom.id}",
            {
                "type": "message_update",
                'sender_name': request.user.get_full_name() or request.user.username,
                'sender_type': 'agent',
                'content': content,
                'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            }
        )

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)