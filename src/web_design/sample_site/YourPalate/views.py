from django.shortcuts import render
import sys
from pathlib import Path
import importlib.util

module_path = Path(__file__).resolve().parent.parent.parent.parent / 'recommender/recommender.py'
print("module_path: ", module_path)
module_name = 'recommender'

spec = importlib.util.spec_from_file_location(module_name, module_path)
recommender_module = importlib.util.module_from_spec(spec)
sys.modules[module_name] = recommender_module
spec.loader.exec_module(recommender_module)

# sys.path.append('/src/recommender')
# print('PATHL ', sys.path)
# from recommender import *
# from django.http import HttpResponse
# from ..src.recommender import recommender


def home(request):
    return render(request, 'home.html')


def quiz(request):
    return render(request, 'quiz.html')


def restrictions(request):
    return render(request, 'restrictions.html')


def results(request):
    output = ['basic sourdough bread', 'berry smash muffins strawberry muffins', 
              'breaded ranch or ranchero chicken', 'chewy macaroons', 
              'christmas rum balls or bourbon balls', 'jello cake', 
              'sourdough bread starter', 'sourdough bread also known as grandma angelitas bread', 
              'sweet butternut squash', 'to die for crock pot roast']
    
    return render(request, 'results.html', {'output': output})


def loading(request):
    return render(request, 'loading.html')


def signUp(request):
    return render(request, 'signUp.html')


def login(request):
    return render(request, 'login.html')
