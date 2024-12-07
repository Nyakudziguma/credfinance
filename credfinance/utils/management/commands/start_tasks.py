from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.core.mail import EmailMessage
from calender.models import Taskboard

class Command(BaseCommand):
    help = 'Start tasks whose start date has arrived'

    def handle(self, *args, **kwargs):
        tasks = Taskboard.objects.filter(start_date__lte=now().date(), status='Open')
        for task in tasks:
            task.status = 'In Progress'
            task.save()

            subject = f'Task "{task.title}" has started!'
            message = f"""
            Hi {task.user.first_name},

            Your task "{task.title}" has started. Please check the task details:

            - Description: {task.description}
            - Start Date: {task.start_date}
            - Due Date: {task.due_date}

            Thank you,
            Credspace Team
            """
            email = EmailMessage(
                subject=subject,
                body=message,
                from_email='noreply@credspace.co.zw',
                to=[task.user.email],
            )
            email.send()

        self.stdout.write(f'{tasks.count()} task(s) started.')
