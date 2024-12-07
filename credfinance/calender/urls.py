from django.urls import path
from . import views
urlpatterns = [
      path('calender', views.calender, name = 'calender'),
       path('taskboard', views.taskboard, name = 'taskboard'),
       path('close-task/<int:task_id>/',views.close_task, name='close_task'),
       path('add-task/', views.add_task, name='add_task'),
        path('edit-task/', views.edit_task, name='edit_task'),
]