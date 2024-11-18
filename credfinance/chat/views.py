import json
from .models import Client, ChatRoom, Message
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404,redirect
from django.db.models import Max
from django.views.decorators.csrf import csrf_exempt
from accounts.models import Account
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.template.loader import render_to_string
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def handle_client_message(phone_number, message_content):
    """
    Handles incoming messages from clients via WhatsApp.
    If the client doesn't exist, creates a new one with the phone number as the name.
    """
    try:
        # Try to get the client based on the phone number
        client = Client.objects.get(phone_number=phone_number)
    except Client.DoesNotExist:
        # If the client does not exist, create a new client with the phone number as the name
        client = Client.objects.create(
            phone_number=phone_number,
            name=phone_number  # Set phone number as the client's name
        )
    
    # Ensure the chatroom is created or fetched for the client with status 'open'
    chatroom, created = ChatRoom.objects.get_or_create(client=client, status='open')

    # Save the message to the database
    message = Message.objects.create(
        chatroom=chatroom,
        sender_type='client',
        sender_id=client.id,
        content=message_content,
    )
    
    return {"success": True, "chatroom_id": chatroom.id, "message_id": message.id}


@login_required
def send_message(request, chatroom_id):
    if request.method == 'POST':
        try:
            chatroom = ChatRoom.objects.get(id=chatroom_id)
            
            # Get the content of the message and ensure it's not empty
            content = request.POST.get('content', '').strip()
            if not content:
                return redirect('chatroom', chatroom_id=chatroom_id)
            
            # Get the sender as the logged-in user's Account
            sender = Account.objects.get(id=request.user.id)

            # Create the message with correct sender reference
            message = Message.objects.create(
                chatroom=chatroom,
                content=content,
                sender_type='agent',
                sender_id=sender.id
            )

            # Update chatroom's latest message and updated_at timestamp
            chatroom.latest_message = message
            chatroom.save()

            # Convert the timestamp to the local time zone
            local_time = timezone.localtime(message.timestamp)
            formatted_timestamp = local_time.strftime('%Y-%m-%d %H:%M:%S')

            # Prepare the message context
            message_context = {
                'message': message,
                'sender_name': sender.first_name,
                'timestamp': formatted_timestamp,
            }

            # Get the channel layer
            channel_layer = get_channel_layer()
            
            # Send to chat room group
            async_to_sync(channel_layer.group_send)(
                f"chat_{chatroom_id}",
                {
                    "type": "chat_message",
                    "message": {
                        'sender_name': sender.first_name,
                        'sender_type': 'agent',
                        'content': content,
                        'timestamp': formatted_timestamp,
                    }
                }
            )

            # Update chatroom list for all users
            chatrooms = ChatRoom.objects.all().order_by('-updated_at')  # Changed from latest_message__timestamp
            async_to_sync(channel_layer.group_send)(
                "chatroom_list",
                {
                    "type": "chatroom_list_update",
                    "html": render_to_string("apps/chatroom_list.html", {"chatrooms": chatrooms})
                }
            )

            # Return only the new message's HTML as a fragment
            return render(request, 'apps/chat_message.html', message_context)
            
        except (ChatRoom.DoesNotExist, Account.DoesNotExist) as e:
            print(f"Error in send_message: {e}")
            return redirect('chatroom', chatroom_id=chatroom_id)
        
    return redirect('chatroom', chatroom_id=chatroom_id)

def chats(request, chatroom_id=None):
    # Fetch all chatrooms for the logged-in user
    chatrooms = ChatRoom.objects.all()
    
    # If a specific chatroom_id is provided, fetch the corresponding chatroom and its messages
    chatrooms = chatrooms.annotate(latest_message_timestamp=Max('messages__timestamp'))

    # Fetch the latest message for each chatroom
    for chatroom in chatrooms:
        chatroom.latest_message = Message.objects.filter(chatroom=chatroom).order_by('-timestamp').first()

    if chatroom_id:
        chatroom = get_object_or_404(ChatRoom, id=chatroom_id)
        messages = Message.objects.filter(chatroom=chatroom).order_by('timestamp')
    else:
        chatroom = None
        messages = []

    # Return chatrooms and the selected chatroom's messages to the template
    return render(request, 'apps/chat.html', {'chatrooms': chatrooms, 'chatroom': chatroom, 'messages': messages})

def chatroom_list_update(self, event):
    # Broadcast the updated list to all connected clients
    chatrooms = self.get_chatrooms()
    html_content = self.render_chatroom_list(chatrooms)  # Render the updated list
    self.send(text_data=json.dumps({
        'type': 'chatroom_list_update',
        'html': html_content
    }))
