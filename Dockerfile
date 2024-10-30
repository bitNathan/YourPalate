# Use the official Python image as a base
FROM python:3.10.12


WORKDIR /home/clear/49595/YourPalate

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Command to run the application
CMD ["python", "src/web_design/sample_site/manage.py", "runserver", "0.0.0.0:8000"]
# gunicorn --bind 0.0.0.0:8000 sample_site.wsgi:application
# CMD ["gunicorn", "sample_site.wsgi:application", "--bind", "0.0.0.0:8000"]
