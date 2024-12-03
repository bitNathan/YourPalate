# YourPalate
_We could insert link to the website here, as an example. Once we get a stable link._

### Warning
This project is written uses Django, specifically in "debug" mode as well, this means the admin poage is accessible from the web with no authentication. Do not host in production environments without disabling this in Djanog's settings.

## Project Abstract
Meal planning and grocery shopping can be time-consuming and overwhelming tasks, particularly for college students. To address this, we propose YourPalate. 

Our ECE 49595O senior design project is an open-source web application that automates the process of meal planning and shopping list creation by utilizing machine learning algorithms, k-nearest neighbors, and public APIs, YourPalate generates personalized weekly meal plans based on user preferences, dietary restrictions, culinary skills, and time constraints. 

Unlike traditional recipe platforms that focus on individual meals, YourPalate integrates user data to produce a balanced and diverse meal schedule that encourages culinary exploration while accommodating time and budget limitations. Additionally, the application offers a seamless user experience with features like ADA-compliant design, downloadable meal plans, and dynamically updated shopping lists. 
We implement YourPalate using Django, TensorFlow, and SQL as the primary technologies, demonstrating its potential as a valuable tool for enhancing dietary habits and simplifying meal preparation

## Admin page
Because our project is in debug mode the admin page is not secure. It can be acccessed by `<DNS NAME>/admin`as opposed to `<DNS NAME>/YourPalate/etc`.

This can be disabled in the project by going into settings.py (contained within the web development folder) and setting DEBUF_MODE to false. While it is available however, the page provides valuable testing information about users.

Here it's possible to see all the accounts that have access through your authentication system, and edit or delete them if necessary.

## User Features
![image](https://github.com/user-attachments/assets/2fd13542-da9d-48d1-9fc3-a96e482d2c51)

_YourPalate register page above_

![image](https://github.com/user-attachments/assets/a4dc1da0-0466-4d3c-9808-a51f62e881b5)

_YourPalate login page above_

After logging in and creating an account if necessary. The user is directed to our home page. This page contains all the links users need to use the program successfully.

![image](https://github.com/user-attachments/assets/764a5976-0778-42d8-a680-dbf8bd8899bb)
_YourPalate home page shown above_

Each user is required to create or log into an account when accessing the website. 

![image](https://github.com/user-attachments/assets/e66a8c76-ad4b-487d-8c15-345ddae2bd4d)

_YourPalate restrictions page shown above_

From there they have the option of selecting restrictions including caloric intake goal, vegetarianism, and time restrictions per meal. 

![image](https://github.com/user-attachments/assets/6ddcc1b7-932c-4d62-9841-10d2328aeaf6)

_YourPalate quiz page shown above_

In addition, they can complete our preferences quiz which gets their opinions on several representative recipes in order to provide initial recommendations.

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
For our implimentation of this project we used the AWS RDS web service to host a database using MySQL. The connection details should be stored in a `.env` file in the root direcoty of the project. If the data is properly formatted then you should be able to connect with no other changes.

#### Data
The data for YourPalate is contained within several tables in our database. (All stored under the parent `User-restrictions`
- recipes
   - Contains recipe name, id, prep-time, nutrition info, user description, ingredients list, cooking instructions, and tags we added to aid in recommendation.
- user_ratings
   - Dual column table where the first column is recipe IDs and the second is a JSON dictionary of each user that has rated that recipe, and what their rating was.
- users_restrictions
   - Contains user ID and the restrictions they've input in that portion of the website.
- new_users
   - Another dual column table formatted the same as user_ratings.
   - Contains user ids and a JSON dictionary of the recipes they've rated alongside the rating itself.
   - Our initial dataset contained user rating data, which is how we generate our recommendations. This file is where we store new user information during deployment.
      - There's nothing stopping someone from integrating these two tables together, however more user data means the recommendations take longer to generate. (Though they're likely more accurate as well.) At some point there needs to be logic so as to not constantly increase runtime during deployment.

## Repository Structure

src is split into two parts
- recommender contains our data processing, recommendation algorithms, and updating for our questionnaire
- web_design/sample_site contains our Django frontend work, major parts include
    - YourPalate/ directory contains our main app functionality
    - templates/ contains all the html files for each webpage in the project
    - staticfiles contains css styles and images that are displayed in our project
    - sampe_site/ contains Django settings that are configured for our deployment, but can be changed to fit your pipeline and needs
