from django.shortcuts import render, redirect

# from authentication tutorial
# https://www.geeksforgeeks.org/user-authentication-system-using-django/
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
# from .models import *


# importing recommender
import sys
from pathlib import Path
import importlib.util

module_path = Path(__file__).resolve().parent.parent.parent.parent / 'recommender/recommender.py'
# print("module_path: ", module_path)
module_name = 'recommender'

spec = importlib.util.spec_from_file_location(module_name, module_path)
recommender_module = importlib.util.module_from_spec(spec)
sys.modules[module_name] = recommender_module
spec.loader.exec_module(recommender_module)


@login_required(login_url='/YourPalate/login/')
def home(request):
    return render(request, 'home.html')


@login_required(login_url='/YourPalate/login/')
def quiz(request):
    return render(request, 'quiz.html')


@login_required(login_url='/YourPalate/login/')
def restrictions(request):
    return render(request, 'restrictions.html')


@login_required(login_url='/YourPalate/login/')
def results(request):

    # running the recommender
    output = recommender_module.run().name.values

    return render(request, 'results.html', {'output': output})


@login_required(login_url='/YourPalate/login/')
def loading(request):
    return render(request, 'loading.html')


'''
Authentication views from
https://www.geeksforgeeks.org/user-authentication-system-using-django/
'''


def login_page(request):
    # Check if the HTTP request method is POST (form submission)
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        # print("username: ", username)

        # Check if a user with the provided username exists
        if not User.objects.filter(username=username).exists():
            # Display an error message if the username does not exist
            messages.error(request, 'Invalid Username')
            return redirect('/YourPalate/login/')

        # Authenticate the user with the provided username and password
        user = authenticate(username=username, password=password)
        # print("user authenticated: ", user)

        if user is None:
            # Display an error message if authentication fails (invalid password)
            messages.error(request, "Invalid Password")
            return redirect('/YourPalate/login/')
        else:
            # print("about to login...")
            # Log in the user and redirect to the home page upon successful login
            login(request, user)
            return redirect('/YourPalate/home/')

    # Render the login page template (GET request)
    return render(request, 'login.html')


def signUp(request):
    # Check if the HTTP request method is POST (form submission)
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check if a user with the provided username already exists
        user = User.objects.filter(username=username)

        if user.exists():
            # Display an information message if the username is taken
            messages.info(request, "Username already taken!")
            return redirect('/YourPalate/signUp/')

        # Create a new User object with the provided information
        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username
        )

        # Set the user's password and save the user object
        user.set_password(password)
        user.save()

        # Display an information message indicating successful account creation
        messages.info(request, "Account created Successfully!")
        return redirect('/YourPalate/signUp/')

    # Render the registration page template (GET request)
    return render(request, 'signUp.html')
