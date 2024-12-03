from django.db import models
from django.utils import timezone
from uuid import uuid4
from chat.models import Client
from django.utils.timezone import now, timedelta

class Intent(models.Model):
    tag = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)  

    def __str__(self):
        return self.tag

class Pattern(models.Model):
    intent = models.ForeignKey(Intent, related_name="patterns", on_delete=models.CASCADE)
    text = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.intent.tag} - {self.text}"

class Response(models.Model):
    intent = models.ForeignKey(Intent, related_name="responses", on_delete=models.CASCADE)
    text = models.TextField()

    def __str__(self):
        return f"{self.intent.tag} - {self.text}"

class Sessions(models.Model):
    user= models.ForeignKey(Client, on_delete=models.CASCADE)
    state = models.CharField(max_length=255, default='menu')
    position = models.CharField(max_length=255, default = 'menu')
    previous_menu =models.CharField(max_length=255, default='menu')
    uniqueId = models.CharField(null=True, blank=True, max_length=100)
    stamp = models.CharField(max_length=255, default = 'menu')
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)
    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        if self.uniqueId is None:
            self.uniqueId = str(uuid4()).split('-')[4]

        self.last_updated = timezone.localtime(timezone.now())
        super(Sessions, self).save(*args, **kwargs)
    def __str__(self):
            return self.uniqueId
    
class Conversation(models.Model):
    user = models.ForeignKey(Client, on_delete=models.CASCADE)  
    start_time = models.DateTimeField(default=now)  
    last_message_time = models.DateTimeField(auto_now=True)  

    def is_active(self):
        """
        Check if the conversation is still active within the 24-hour window.
        """
        return now() - self.start_time <= timedelta(hours=24)