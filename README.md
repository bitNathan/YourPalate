# Your Palate
_We could insert link to the website here, as an example. Once we get a stable link._

## Project Abstract
Meal planning and grocery shopping can be time-consuming and overwhelming tasks, particularly for college students. To address this, we propose YourPalate. 

Our ECE 49595O senior design project is an open-source web application that automates the process of meal planning and shopping list creation by utilizing machine learning algorithms, k-nearest neighbors, and public APIs, YourPalate generates personalized weekly meal plans based on user preferences, dietary restrictions, culinary skills, and time constraints. 

Unlike traditional recipe platforms that focus on individual meals, YourPalate integrates user data to produce a balanced and diverse meal schedule that encourages culinary exploration while accommodating time and budget limitations. Additionally, the application offers a seamless user experience with features like ADA-compliant design, downloadable meal plans, and dynamically updated shopping lists. 
We implement YourPalate using Django, TensorFlow, and SQL as the primary technologies, demonstrating its potential as a valuable tool for enhancing dietary habits and simplifying meal preparation

## Admin page
Because our project is in debug mode the admin page is not secure, but we'll mention setup while in deployment here

## User Features
Each user is required to create or log into an account when accessing the website. 
From there they have the option of selecting restrictions including caloric intake goal, vegetarianism, and time restrictions per meal. In addition, they can complete our preferences quiz which gets their opinions on several representative recipes in order to provide initial recommendations.

Note, if the user tries to generate recommendations without any preferences or restrictions input they will not be tailored to that user's tastes.

After optionally filling out this information they can use the generate mealplan functionality to create a mealplan and recipe for the week.

## Deployment
YourPalate is meant to be deployed to an AWS EC2 instance, and interact with an RDS MySQL databse.

To deploy the project...
1. Clone the repository into an EC2 instance
2. run `./setup_docker` script found in the scripts directory
3. Update `nginx.conf` file in the root directory to reflect your IP and port (default is 8000)
4. Use `sudo docker compose up -d` to create and deploy the necessary image
5. The website should then be accessible from the http://<DNS_name> which is accessible from the AWS interface
   
### Setup/Integrate database
Still in development, we'll add steps here like above

## Repository Structure

src is split into two parts
- recommender contains our data processing, recommendation algorithms, and updating for our questionnaire
- web_design/sample_site contains our Django frontend work, major parts include
    - YourPalate/ directory contains our main app functionality
    - templates/ contains all the html files for each webpage in the project
    - staticfiles contains css styles and images that are displayed in our project
    - sampe_site/ contains Django settings that are configured for our deployment, but can be changed to fit your pipeline and needs
