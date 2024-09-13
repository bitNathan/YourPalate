from django.urls import path
from . import views

urlpatterns = [
    path("intro/", views.intro, name="intro"),
    path("loading/", views.loading, name="loading"),
    path("restrictions/", views.restrictions, name="restrictions"),
    path("quiz/", views.quiz, name="quiz"),
    path("results/", views.results, name="results"),
]