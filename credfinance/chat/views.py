import json
from .models import Client, ChatRoom, Message
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404,redirect
from django.db.models import Max
from django.views.decorators.csrf import csrf_exempt
from accounts.models import Account
from django.contrib.auth.decorators import login_required
from django.utils import timezone


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
        
        chatroom = ChatRoom.objects.get(id=chatroom_id)
        
        # Get the content of the message and ensure it's not empty
        content = request.POST.get('content', '').strip()
        if not content:
            return redirect('chatroom', chatroom_id=chatroom_id)  # Optionally, add a message about empty content
        
        # Get the sender as the logged-in user’s Account
        sender = Account.objects.get(id=request.user.id)

        # Create the message with correct sender reference
        message = Message.objects.create(
            chatroom=chatroom,
            content=content,
            sender_type='agent',  # You can make this dynamic if needed
            sender_id=sender.id
        )

        # Convert the timestamp to the local time zone
        local_time = timezone.localtime(message.timestamp)
        formatted_timestamp = local_time.strftime('%Y-%m-%d %H:%M:%S')

        # Return only the new message's HTML as a fragment to be appended in the chat
        return render(request, 'apps/chat_message.html', {
            'message': message,
            'sender_name': sender.first_name,
            'timestamp': formatted_timestamp,
        })
        
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

