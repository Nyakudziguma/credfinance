from django.urls import path
from . import views
urlpatterns = [
      path('bwm', views.bulk_messaging, name = 'bwm'),
      path('send_messages', views.send_messages, name = 'send_messages'),

]