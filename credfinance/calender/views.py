from django.shortcuts import render

# Create your views here.
from django.shortcuts import render


def calender(request,):
    return render(request, 'apps/calender.html',)

def taskboard(request,):
    return render(request, 'apps/taskboard.html',)