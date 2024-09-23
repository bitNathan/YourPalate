from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render


def intro(request):
    return render(request, 'intro.html')

def quiz(request):
    return render(request, 'quiz.html')

def restrictions(request):
    return render(request, 'restrictions.html')

def results(request):
    return render(request, 'results.html')

def loading(request):
    return render(request, 'loading.html')