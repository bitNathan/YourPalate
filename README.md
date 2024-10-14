# Your Palate 
### Django test instructions

*Two scripts in the scripts folder should be run*
    
    1. vm_django_activate sets up the virtual machine
    2. django_runserver runs manage.py runserver for testing

##### Errors
    - if you get something saying a character isn't recognized dos2unix "filename" usually works
    - unauthorized fixed by using chmod +x "filename" (should be set up already but just in case)

##### [Django Tutorial Source](https://docs.djangoproject.com/en/5.0/intro/tutorial01/)
This is what I used to set up the website, it's fairly simple.

### AWS connection steps
Follow these steps to successfully link AWS instance:

    cd ~/YourPalate/src/web_design/sample_site/sample_site
    sudo nano settings.py

Change/ edit allowed hosts list to include Public IP address and Public IPv4 DNS. Save and exit.

    cd /etc/nginx/sites-available
    sudo nano sample_site

Change/ edit server_name to include Public IP address and Public IPv4 DNS. Save and exit.

    sudo rm /etc/nginx/sites-enabled/sample_site
    sudo ln -s /etc/nginx/sites-available/sample_site /etc/nginx/sites-enabled

If file already exists error shows try below command line
    
    sudo rm /etc/nginx/sites-enabled/sample_site

Initiate/ reinitiate nginx link

    sudo nginx -t
    sudo systemctl restart nginx
    cd ~/YourPalate/src/web_design/sample_site
    gunicorn --bind 0.0.0.0:8000 sample_site.wsgi:application

Now run http address link for the Public IPv4 DNS with "/YourPalate/home/" attached at the end.
For example: "http://ec2-18-223-133-155.us-east-2.compute.amazonaws.com/YourPalate/home/"



    
