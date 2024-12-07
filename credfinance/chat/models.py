from django.db import models
from accounts.models import Account, Company

class Client(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255, unique=True) 
    email = models.EmailField(blank=True, null =True) 
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name


class ChatRoom(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
    ]

    agent = models.ForeignKey(Account, on_delete=models.SET_NULL, related_name='agent_chatrooms', null=True, blank=True )
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='client_chatrooms')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    latest_message = models.ForeignKey(
        'Message',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='latest_message_chatrooms'
    )


    def __str__(self):
        return f" Client: {self.client.name}"

    @classmethod
    def get_or_create_room(cls, agent, client):
        room, created = cls.objects.get_or_create(agent=agent, client=client)
        return room

class Message(models.Model):
    chatroom = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
    sender_type = models.CharField(max_length=10, choices=[('agent', 'Agent'), ('client', 'Client')])
    sender_id = models.PositiveIntegerField()  
    content = models.TextField(blank=True, null=True)
    image = models.FileField(upload_to='chat_files/', blank=True, null=True) 
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)


    def __str__(self):
        return f"Message {self.id} in ChatRoom {self.chatroom.id}"

    @property
    def sender(self):
        if self.sender_type == 'agent':
            return Account.objects.get(id=self.sender_id)
        elif self.sender_type == 'client':
            return Client.objects.get(id=self.sender_id)

class Attachment(models.Model):
    message = models.ForeignKey(Message, related_name='attachments', on_delete=models.CASCADE)
    file = models.FileField(upload_to='attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment {self.id} for Message {self.message.id}"
