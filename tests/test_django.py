from unittest import TestCase as tc
from django.test import Client




class TestDjango(tc):
    
    
    def test_django_intro(self):
        # run_django_server()
        client = Client()
        response = client.get("http://127.0.0.1:8000/initialApp/intro/")
        assert response.status_code == 200, "Failed to connect to Django server"
        
    def test_django_quiz(self):
        client = Client()
        response = client.get("http://127.0.0.1:8000/initialApp/intro/")
        assert response.status_code == 200, "Failed to connect to Django server"
    def test_django_restrictions(self):
        client = Client()
        response = client.get("http://127.0.0.1:8000/initialApp/restrictions/")
        assert response.status_code == 200, "Failed to connect to Django server"
    def test_django_results(self):
        client = Client()
        response = client.get("http://127.0.0.1:8000/initialApp/results/")
        assert response.status_code == 200, "Failed to connect to Django server"
    def test_django_loading(self):
        client = Client()
        response = client.get("http://127.0.0.1:8000/initialApp/loading/")
        assert response.status_code == 200, "Failed to connect to Django server"
    def false_test(self):
        client = Client()
        response = client.get("http://127.0.0.1:8000/fakeUrl")
        assert response.status_code == 404, "Did not return 404 for fake URL"
        
    def run_django_server():
        try:
            result = subprocess.run(["/bin/bash", "django_runserver"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(result.stdout.decode())
        except subprocess.CalledProcessError as e:
            print(f"Failed to run django_runserver script: {e.stderr.decode()}")

if __name__ == '__main__':
    test_django_connection()