from django.db import models
from accounts.models import Account

class Client(models.Model):
    client_id = models.CharField(max_length=100, unique=True)  
    name = models.CharField(max_length=255)
    contact_info = models.CharField(max_length=255, blank=True, null=True)  
    def __str__(self):
        return self.name


class ChatRoom(models.Model):
    agent = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='agent_chatrooms')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='client_chatrooms')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"ChatRoom {self.id} - Agent: {self.agent.username}, Client: {self.client.name}"


class Message(models.Model):
    chatroom = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
    sender_type = models.CharField(max_length=10, choices=[('agent', 'Agent'), ('client', 'Client')])
    sender_id = models.PositiveIntegerField()  
    content = models.TextField()
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
