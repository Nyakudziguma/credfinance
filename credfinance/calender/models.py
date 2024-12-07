from django.db import models
from accounts.models import Account
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now

class Taskboard(models.Model):
    STATUS_TYPES = [
        ('Open', 'Open'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed')
    ]
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=255, choices=STATUS_TYPES)

    def mark_as_started(self):
        if self.start_date <= now().date() and self.status == 'Open':
            self.status = 'In Progress'
            self.save()

    def __str__(self):
        return self.title