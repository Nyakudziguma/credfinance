from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils import timezone
from asgiref.sync import async_to_sync
from django.template.loader import render_to_string
from chat.models import Client, ChatRoom, Message
from balances.models import CompanyBalance
from bot.models import Conversation
from channels.layers import get_channel_layer

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from accounts.models import CompanyAuthentication

class CustomTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.headers.get("Authorization")
        if not token:
            return None  
        
        try:
            api_token = CompanyAuthentication.objects.get(meta_token=token)  
        except CompanyAuthentication.DoesNotExist:
            raise AuthenticationFailed("Invalid token")

        return (api_token, None)  

class HandleClientMessageView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = [CustomTokenAuthentication]

    def post(self, request):
        """
        Handles incoming client messages via API.
        """
        try:
            phone_number = request.data.get('phone_number')
            message_content = request.data.get('message_content')
            image = request.FILES.get('image')

            if not phone_number:
                return Response(
                    {"success": False, "error": "Phone number ais required."},
                    status=400
                )

            try:
                client = Client.objects.get(phone_number=phone_number)
                company = client.company
            except Client.DoesNotExist:
                client = Client.objects.create(
                    phone_number=phone_number,
                    name=phone_number
                )
                company = None  

            chatroom, created = ChatRoom.objects.get_or_create(client=client, status='open')

            message = Message.objects.create(
                chatroom=chatroom,
                content=message_content,
                image=image if image else None,
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
                    'content': message_content,
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
                        'content': message_content,
                        'timestamp': formatted_timestamp,
                        "image_url": message.image.url if message.image else None,
                    }
                }
            )

            async_to_sync(channel_layer.group_send)(
                "chat_updates",
                {
                    "type": "chat_update",
                    "chatroom_id": chatroom.id,
                    "message_content": message_content,
                    "timestamp": formatted_timestamp,
                    "sender_name": client.name
                }
            )

            total_chatrooms = ChatRoom.objects.count()
            total_messages = Message.objects.count()
            unread_messages = Message.objects.filter(is_read=False).count()
            read_messages = Message.objects.filter(is_read=True).count()
            total_users = Client.objects.filter(company=company).count() if company else 0
            company_balance = CompanyBalance.objects.get(company=company) if company else None
            balance = str(company_balance.balance) if company_balance else "N/A"
            conversations = Conversation.objects.filter(user__company=company).count()
            

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
                    'conversations': conversations
                }
            )

            return Response({
                "success": True,
                "chatroom_id": chatroom.id,
                "message_id": message.id,
                "html": html_message
            }, status=200)

        except Exception as e:
            print(f"Error in HandleClientMessageView: {e}")
            return Response(
                {"success": False, "error": str(e)},
                status=500
            )
