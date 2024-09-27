from django.urls import path
from . import views

urlpatterns = [
    path("home/", views.home, name="home"),
    path("loading/", views.loading, name="loading"),
    path("restrictions/", views.restrictions, name="restrictions"),
    path("quiz/", views.quiz, name="quiz"),
    path("results/", views.results, name="results"),
    path("login/", views.login, name="login"),
    path("signUp/", views.signUp, name="signUp"),
]