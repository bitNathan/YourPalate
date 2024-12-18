from django.urls import path
from . import views

# commented imports / code from authentication tutorial
# https://www.geeksforgeeks.org/user-authentication-system-using-django/
# from django.contrib import admin
# from django.conf import settings

urlpatterns = [
    path("home/", views.home, name="home"),
    path("loading/", views.loading, name="loading"),
    path("restrictions/", views.restrictions, name="restrictions"),
    path("quiz/", views.quiz, name="quiz"),
    path("results/", views.results, name="results"),
    path("login/", views.login_page, name="login"),
    path("signUp/", views.signUp, name="signUp"),
    path("save_preferences/", views.save_preferences, name="save_preferences"),
    path("save_restrictions/", views.save_restrictions, name="save_restrictions"),
    path("help/", views.help, name="help"),
]

# TODO maybe adds css and image functionality
# (also from authentication tutorial)
'''
# may or may not be needed
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serve static files using staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()
'''
