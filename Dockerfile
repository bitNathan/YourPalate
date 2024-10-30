# Use the official Python image as a base
FROM python:3.10.12

# Set the working directory in the container
WORKDIR /home/clear/49595/YourPalate

# Copy requirements.txt and install dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Expose the port your app runs on (default is 8000 for Django)
EXPOSE 8000

# Command to run the application
CMD ["python", "src/web_design/sample_site/manage.py", "runserver", "0.0.0.0:8000"]
