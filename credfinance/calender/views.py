from django.shortcuts import render
from .models import Taskboard
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage


@login_required
def calender(request,):
    return render(request, 'apps/calender.html',)

@login_required
def taskboard(request,):
    open_tasks = Taskboard.objects.filter(user=request.user, status__in=['Open', 'In Progress'])

    status_colors = {
        'Open': 'bg-info',
        'In Progress': 'bg-warning',
        'Completed': 'bg-success'
    }
    for task in open_tasks:
        task.color = status_colors.get(task.status, 'bg-secondary')

    return render(request, 'apps/taskboard.html', {'open_tasks': open_tasks,})

@login_required
def close_task(request, task_id):
    if request.method == 'POST':
        try:
            task = Taskboard.objects.get(id=task_id, user=request.user)
            task.status = 'Completed'
            task.save()
            return JsonResponse({'success': True})
        except Taskboard.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Task not found'}, status=404)
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


@login_required
def add_task(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        start_date = request.POST.get('start_date')
        due_date = request.POST.get('due_date')

        if not (title and description and start_date and due_date):
            return JsonResponse({'success': False, 'message': 'All fields are required.'})

        # Save the task
        task = Taskboard.objects.create(
            user=request.user,
            title=title,
            description=description,
            start_date=start_date,
            due_date=due_date,
            status='Open'
        )

        # Send email notification
        email_subject = "New Task Created: {}".format(title)
        email_body = (
            f"Hi {request.user.first_name},\n\n"
            f"You have successfully created a new task:\n\n"
            f"Title: {title}\n"
            f"Description: {description}\n"
            f"Start Date: {start_date}\n"
            f"Due Date: {due_date}\n\n"
            f"Thank you!"
        )

        email = EmailMessage(
            email_subject,
            email_body,
            to=[request.user.email]
        )

        try:
            email.send()
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error sending email: {str(e)}'})

        return JsonResponse({'success': True, 'message': 'Task created and email sent successfully.'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

@login_required
def edit_task(request):
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        title = request.POST.get('title')
        description = request.POST.get('description')
        start_date = request.POST.get('start_date')
        due_date = request.POST.get('due_date')

        try:
            task = Taskboard.objects.get(id=task_id, user=request.user)
            task.title = title
            task.description = description
            task.start_date = start_date
            task.due_date = due_date
            task.save()

            return JsonResponse({'success': True, 'message': 'Task updated successfully.'})
        except Taskboard.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Task not found.'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})
