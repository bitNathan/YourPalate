from unittest import TestCase as tc
from django.urls import reverse
from django.test import Client
from django.contrib.auth.models import User

# TODO all tests should result in failed login, unless
# self.client.login(username=self.username, password=self.password)


class TestDjango(tc):

    def test_login_redirect(self):
        client = Client()

        # Check if the user is redirected to the login page
        response = client.get(reverse('home'))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login') + '?next=' + reverse('home'), 'response: ' + str(response))

    def test_incorrect_login(self):
        client = Client()

        response = client.post(reverse('login'), {'username': 'wrong', 'password': 'fake'})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'), 'response: ' + str(response))

        # make sure we still get redirected
        self.test_login_redirect()

    # TODO test registration / signUp

    def test_correct_login(self):
        client = Client()
        # Create a temporary user
        self.username = 'test'
        self.password = 'test'
        User.objects.create_user(username=self.username, password=self.password)

        # Log in the temporary user
        response = client.post(reverse('login'), {'username': 'test', 'password': 'test'})

        # Check if the user is redirected to the home page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'), 'response: ' + str(response))

        # Remove the temporary user after the test
        User.objects.filter(username=self.username).delete()

        # TODO test other normal pages
