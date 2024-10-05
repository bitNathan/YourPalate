from django.shortcuts import render
# from django.http import HttpResponse


def home(request):
    return render(request, 'home.html')


def quiz(request):
    return render(request, 'quiz.html')


def restrictions(request):
    return render(request, 'restrictions.html')


def results(request):
    return render(request, 'results.html')


def loading(request):
    return render(request, 'loading.html')


def signUp(request):
    return render(request, 'signUp.html')


def login(request):
    return render(request, 'login.html')
