from unittest import TestCase as tc
from django.test import Client


class TestDjango(tc):
    
    def test_django_intro(self):
        # run_django_server()
        client = Client()
        response = client.get("http://127.0.0.1:8000/YourPalate/home/")
        assert response.status_code == 200, "Failed to connect to Django server"
    
    
    def test_django_quiz(self):
        client = Client()
        response = client.get("http://127.0.0.1:8000/YourPalate/quiz/")
        assert response.status_code == 200, "Failed to connect to Django server"
    
    
    def test_django_restrictions(self):
        client = Client()
        response = client.get("http://127.0.0.1:8000/YourPalate/restrictions/")
        assert response.status_code == 200, "Failed to connect to Django server"
    
    
    def test_django_results(self):
        client = Client()
        response = client.get("http://127.0.0.1:8000/YourPalate/results/")
        assert response.status_code == 200, "Failed to connect to Django server"
    
    
    def test_django_loading(self):
        client = Client()
        response = client.get("http://127.0.0.1:8000/YourPalate/loading/")
        assert response.status_code == 200, "Failed to connect to Django server"
    
    
    def test_django_login(self):
        client = Client()
        response = client.get("http://127.0.0.1:8000/YourPalate/login/")
        assert response.status_code == 200, "Failed to connect to Django server"
    
    
    def test_django_signUp(self):
        client = Client()
        response = client.get("http://127.0.0.1:8000/YourPalate/signUp/")
        assert response.status_code == 200, "Failed to connect to Django server"
    
    
    def test_fake_url(self):
        client = Client()
        response = client.get("http://127.0.0.1:8000/fakeUrl")
        assert response.status_code == 404, "Did not return 404 for fake URL"

if __name__ == '__main__':
    test_django_connection()