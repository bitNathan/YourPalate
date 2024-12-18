from django.shortcuts import render, redirect
import pandas as pd
from django.http import FileResponse

# from authentication tutorial
# https://www.geeksforgeeks.org/user-authentication-system-using-django/
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

# importing recommender
import sys
from pathlib import Path
import importlib.util
import os

module_path = Path(__file__).resolve().parent.parent.parent.parent
# print("module_path: ", module_path)

# make sure first line imports correctly
spec = importlib.util.spec_from_file_location('recommender', os.path.join(module_path, 'recommender', 'recommender.py'))
recommender_module = importlib.util.module_from_spec(spec)
sys.modules['recommender'] = recommender_module
spec.loader.exec_module(recommender_module)

# importing questionnaire
spec = importlib.util.spec_from_file_location(
    'questionnaire', os.path.join(module_path, 'recommender', 'questionnaire.py'))
questionnaire_module = importlib.util.module_from_spec(spec)
sys.modules['questionnaire'] = questionnaire_module
spec.loader.exec_module(questionnaire_module)

# importing db
spec = importlib.util.spec_from_file_location('db', os.path.join(module_path, 'db.py'))
db_module = importlib.util.module_from_spec(spec)
sys.modules['db'] = db_module
spec.loader.exec_module(db_module)


def generate_shopping_list_pdf(shopping_list):
    """Generate a PDF containing the shopping list."""

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setFont("Helvetica", 12)

    pdf.drawString(100, 750, "Your Shopping List:")
    y_position = 730
    for item in shopping_list:
        if y_position < 50:
            pdf.showPage()
            pdf.setFont("Helvetica", 12)
            y_position = 750
        pdf.drawString(100, y_position, f"- {item}")
        y_position -= 20

    pdf.save()
    buffer.seek(0)

    return buffer


@login_required(login_url='/YourPalate/login/')
def home(request):
    return render(request, 'home.html', {'username': request.user.username})


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

    recipes = []
    for recipe in selected_recipes['all_selected_recipes']:
        # replace if description not there or too short
        if type(recipe['description']) is not str or len(recipe['description']) < 30:
            recipe['description'] = 'Sorry! We couldn\'t find a description in our database.'
        recipes.append([recipe['id'], recipe['name'], recipe['description']])

    # print("quiz recipes: ", recipes)
    return render(request, 'quiz.html', {'recipes': recipes})


@login_required(login_url='/YourPalate/login/')
def save_preferences(request):
    if request.method == 'POST':
        # assertions
        # preferences = list of 'like' / 'dislike' / '' in order of presentation
        preferences = request.POST.getlist('preferences')
        recipes = request.POST.getlist('recipes')
        try:
            assert len(preferences) == len(recipes)
        except AssertionError:
            print("preferences:", len(preferences))
            print("recipes:", len(recipes))
            raise ValueError("Length of preferences and recipes must be the same")
        # print("recipes: ", recipes)

        # print("preferences: ", preferences)
        likes_ids = [int(recipes[i]) for i in range(len(preferences)) if preferences[i] == 'like']
        dislikes_ids = [int(recipes[i]) for i in range(len(preferences)) if preferences[i] == 'dislike']
        # print("type: ", type(likes_ids))
        # print("likes: ", likes_ids)
        # print("dislikes: ", dislikes_ids)

        # save likes and dislikes to database
        existing_user_ratings = db_module.get_new_user_ratings(username=request.user.username)
        preferences_json = {recipe_id: 5 for recipe_id in likes_ids}
        preferences_json.update({recipe_id: 1 for recipe_id in dislikes_ids})

        # print("preferences_json: ", preferences_json)

        if (existing_user_ratings is None):
            # user_id = db_module.add_user_restrictions(vegetarian=False, calories=2000, max_time=60)  # Example values
            db_module.add_new_user(username=request.user.username, user_ratings=preferences_json)
        else:
            db_module.update_new_user_ratings(username=request.user.username, new_ratings=preferences_json)

    # always redirect to home page
    return redirect('/YourPalate/home/')


@login_required(login_url='/YourPalate/login/')
def restrictions(request):
    return render(request, 'restrictions.html')


@login_required(login_url='/YourPalate/login/')
def save_restrictions(request):
    if request.method == 'POST':
        dietary_restrictions = request.POST.get('dietary_restrictions')
        time_restrictions = request.POST.get('time_restrictions')
        caloric_intake = request.POST.get('caloric_intake')

        # Convert form values to appropriate types
        vegetarian = dietary_restrictions == 'vegetarian'
        max_time = {
            'none': 0,
            '5_min': 5,
            '20_min': 20,
            '1_hour': 60,
            'more_1_hour': 120
        }.get(time_restrictions, 0)
        calories = int(caloric_intake)

        # Save to database
        existing_restrictions = db_module.get_user_restrictions(username=request.user.username)

        if existing_restrictions is None:
            db_module.add_user_restrictions(
                username=request.user.username,
                vegetarian=vegetarian,
                calories=calories,
                max_time=max_time
            )
        db_module.update_user_restrictions(
            username=request.user.username,
            vegetarian=vegetarian,
            calories=calories,
            max_time=max_time
        )

    return redirect('/YourPalate/home/')


@login_required(login_url='/YourPalate/login/')
def results(request):
    # running the recommender
    similar_users, recommendations, shopping_list = recommender_module.run(username=request.user.username)

    # Check if the request is for downloading the shopping list PDF
    if 'download' in request.GET:
        pdf_buffer = generate_shopping_list_pdf(shopping_list)

        # Serve the PDF file
        return FileResponse(pdf_buffer, as_attachment=True, filename="shopping_list.pdf")

    # Render the results page
    return render(request, 'results.html', {
        'recommendations': recommendations,
        'shopping_list': shopping_list
    })


@login_required(login_url='/YourPalate/login/')
def loading(request):
    return render(request, 'loading.html')


def help(request):
    return render(request, 'help.html')


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
