from django.shortcuts import render, redirect
import pandas as pd

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
import os

module_path = Path(__file__).resolve().parent.parent.parent.parent / 'recommender'
# print("module_path: ", module_path)

# TODO cant test right now because of data issues
# make sure first line imports correctly
spec = importlib.util.spec_from_file_location('recommender', os.path.join(module_path, 'recommender.py'))
recommender_module = importlib.util.module_from_spec(spec)
sys.modules['recommender'] = recommender_module
spec.loader.exec_module(recommender_module)

spec = importlib.util.spec_from_file_location('questionnaire', os.path.join(module_path, 'questionnaire.py'))
questionnaire_module = importlib.util.module_from_spec(spec)
sys.modules['questionnaire'] = questionnaire_module
spec.loader.exec_module(questionnaire_module)


@login_required(login_url='/YourPalate/login/')
def home(request):
    return render(request, 'home.html')


@login_required(login_url='/YourPalate/login/')
def quiz(request):
    # getting recipes to be rated
    # everything from questionnaire.py / copied from the if __name__ == "__main__": block
    path = Path(__file__).resolve().parent.parent.parent.parent.parent

    recipes = pd.read_csv(os.path.join(path, "data/filtered_recipes_clustered.csv"))
    recipes = recipes[["name", "id", "cluster", "description"]].to_dict(orient="records")

    groups = questionnaire_module.group_recipes(recipes, "cluster")
    group_weights = {group: 1.0 for group in groups.keys()}

    selected_recipes = questionnaire_module.get_recipes_for_review(groups, group_weights=group_weights, num_recipes=10)

    # TODO output all lowercase, would be ncie to uppercase some words
    # maybe do in the data itself rather than here to reduce runtime
    recipes = []
    for recipe in selected_recipes['all_selected_recipes']:
        # replace if description not there or too short
        if type(recipe['description']) is not str or len(recipe['description']) < 30:
            recipe['description'] = 'Sorry! We couldn\'t find a description in our database.'
        recipes.append([recipe['id'], recipe['name'], recipe['description']])

    # print("recipes: ", recipes)
    return render(request, 'quiz.html', {'recipes': recipes})


@login_required(login_url='/YourPalate/login/')
def save_preferences(request):
    # TODO save to sql database under user
    if request.method == 'POST':
        # preferences = list of 'like' / 'dislike' / '' in order of presentation
        preferences = request.POST.getlist('preferences')
        recipes = request.POST.getlist('recipes')
        try:
            assert len(preferences) == len(recipes)
        except AssertionError:
            print("preferences:", len(preferences))
            print("recipes:", len(recipes))
            raise ValueError("Length of preferences and recipes must be the same")
        print('debugging info for save_preferences')
        # print("preferences: ", preferences)
        # print("recipes: ", recipes)

        likes = [int(recipe['id']) for recipe in recipes if preferences[recipes.index(recipe)] == 'likes']
        dislikes = [int(recipe['id']) for recipe in recipes if preferences[recipes.index(recipe)] == 'dislikes']

        print("likes: ", likes)
        print("dislikes: ", dislikes)
        print("recipes: ", recipes)

    return redirect('/YourPalate/home/')


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
