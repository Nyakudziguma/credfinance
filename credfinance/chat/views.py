
# from rest_framework.views import APIView
# from rest_framework import generics, status
# from rest_framework.response import Response
# from .models import ChatRoom, Message, Client
# from .serializers import ChatRoomSerializer, MessageSerializer
# from django.contrib.auth.models import User
# from .pusher import pusher_client

# class ChatRoomListCreateView(generics.ListCreateAPIView):
#     queryset = ChatRoom.objects.all()
#     serializer_class = ChatRoomSerializer

#     def perform_create(self, serializer):
#         serializer.save()

# class MessageListCreateView(APIView):
#     def get(self, request, chatroom_id):
#         messages = Message.objects.filter(chatroom_id=chatroom_id).order_by('timestamp')
#         serializer = MessageSerializer(messages, many=True)
#         return Response(serializer.data)

#     def post(self, request, chatroom_id):
#         data = request.data
#         data['chatroom'] = chatroom_id
#         serializer = MessageSerializer(data=data)
#         if serializer.is_valid():
#             message = serializer.save()
            
#             # Trigger Pusher event for real-time updates
#             pusher_client.trigger(f'chat_{chatroom_id}', 'new_message', {
#                 'id': message.id,
#                 'chatroom': chatroom_id,
#                 'sender_type': message.sender_type,
#                 'sender_id': message.sender_id,
#                 'content': message.content,
#                 'timestamp': message.timestamp.isoformat(),
#                 'is_read': message.is_read
#             })
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from django.shortcuts import render


def chats(request,):
    return render(request, 'apps/chat.html',)