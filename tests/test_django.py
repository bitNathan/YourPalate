from unittest import TestCase as tc
from django.urls import reverse
from django.test import Client


class TestDjango(tc):

    def test_django_home(self):
        # run_django_server()
        client = Client()
        response = client.get(reverse("home"))
        assert response.status_code == 200, "Failed to connect to Django server"

    def test_django_quiz(self):
        client = Client()
        response = client.get(reverse("quiz"))
        assert response.status_code == 200, "Failed to connect to Django server"

    def test_django_restrictions(self):
        client = Client()
        response = client.get(reverse("restrictions"))
        assert response.status_code == 200, "Failed to connect to Django server"

    # NOT TESTED: results runs model which requires data to be extracted from the zip
    #    file which is not possible in the test environment
    # def test_django_results(self):
    #     client = Client()
    #     response = client.get("http://127.0.0.1:8000/YourPalate/results/")
    #     assert response.status_code == 200, "Failed to connect to Django server"

    def test_django_loading(self):
        client = Client()
        response = client.get(reverse("loading"))
        assert response.status_code == 200, "Failed to connect to Django server"

    def test_django_login(self):
        client = Client()
        response = client.get(reverse("login"))
        assert response.status_code == 200, "Failed to connect to Django server"

    def test_django_signUp(self):
        client = Client()
        response = client.get(reverse("signUp"))
        assert response.status_code == 200, "Failed to connect to Django server"

    def test_fake_url(self):
        client = Client()
        response = client.get("http://127.0.0.1:8000/fakeUrl")
        assert response.status_code == 404, "Did not return 404 for fake URL"
