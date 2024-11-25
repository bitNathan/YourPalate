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
        username = 'login_test_user'
        password = 'login_test_password'

        # delete test user if it exists
        User.objects.filter(username=username).delete()

        # Create a temporary user
        User.objects.create_user(username=username, password=password)

        # test login
        response = client.post(reverse('login'), {'username': username, 'password': password})

        # delete user
        User.objects.filter(username=username).delete()

        # Check if the user is redirected to the home page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'), 'response: ' + str(response))

    def helper_page_access_after_login(self, page):
        client = Client()
        username = str(page) + '_test_user'
        password = str(page) + '_test_password'

        # delete test user if it exists
        User.objects.filter(username=username).delete()

        # Create a temporary user
        User.objects.create_user(username=username, password=password)

        # login
        client.post(reverse('login'), {'username': username, 'password': password})

        # test page access
        response = client.get(reverse(page))
        assert response.status_code == 200, "Failed to connect to " + page + " page"

        # delete user
        User.objects.filter(username=username).delete()

    # TODO depends on data, not in CI testing env yet
    # def test_quiz_page_access_after_login(self):
    #     self.helper_page_access_after_login('quiz')

    def test_home_page_access_after_login(self):
        self.helper_page_access_after_login('home')

    # def test_results_page_access_after_login(self):
    #     # TODO: runs recommender, takes time, needs data access,
    #     #   and recommemnder output to be tested
    #     self.helper_page_access_after_login('results')

    def test_restrictions_page_access_after_login(self):
        self.helper_page_access_after_login('restrictions')


    def test_help_page_access_after_login(self):
        self.helper_page_access_after_login('help')

