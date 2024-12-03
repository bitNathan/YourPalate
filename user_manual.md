# User Manual
## Generating your First Meal Plan

### Logging in
 Every user is greeted with the login page upon visiting the website. If you have an account, input the associated username and password to access the hone page.
 
![image](https://github.com/user-attachments/assets/a4dc1da0-0466-4d3c-9808-a51f62e881b5)

_YourPalate login page above_

If you don't yet have an account, register by following the "Register" link on the login page, and filling out the fields in the register page shown below.

![image](https://github.com/user-attachments/assets/2fd13542-da9d-48d1-9fc3-a96e482d2c51)

_YourPalate register page above_

Upon successfully logging in, users will be met at our home screen. From here there are three accessible pages, using each is described below.

![image](https://github.com/user-attachments/assets/764a5976-0778-42d8-a680-dbf8bd8899bb)

_YourPalate home page above_

### Restrictions

![image](https://github.com/user-attachments/assets/e66a8c76-ad4b-487d-8c15-345ddae2bd4d)

_YourPalate restrictions page shown above_

Here, each user is required to provide 
- The amount of aclories they typically eat, or would like to aim for in the duration of our mealplan. (If you're unsure how many calories you eat, or should be eating, [this Calorie Calculator](https://www.calculator.net/calorie-calculator.html) as a starting point)
- Any dietary restrictions they wish to accomodate from our dropdown list.
- Any time restrictions, or how long the you're is willing to spend to cook each meal of the day.

Each of these preferences is necessary as we filter recipes from our dataset to be excluded from our recommendation algorithm, ensuring you meet every individual preference.

As soon as you submit them, they are saved in our database in your specific accout.

### Preferences Quiz

![image](https://github.com/user-attachments/assets/6ddcc1b7-932c-4d62-9841-10d2328aeaf6)

_YourPalate quiz page shown above_

The first time you use our recommendation quiz our algorithm will gather several recipes with the goal of giving you diverse and representative options to best convey your unique palate.

Simply go through each element in the table and select like or dislike. (or don't select anything and we'll keep it neutral)

Once again, as soon as you hit the submit button, these preferences will be saved tyo our database to form the basis of all sbsequent recommendations.

### Plan Generation

After you've completed the previouse two steps of speficying preferences and restrictions, you can generate your meal plan!

The actual process is completely automated, and completed as soon as you press the "Generate Mealplan" button.
- Note: If you don't specify any restrictions or preferences, then your meal plan will essentially be random, otherwise it's custom to you.

After the meal plan is generated it will be presented back to you in a table, and you'll have the chance to regenerate any meal, if it's something you don't like.
- This both replaces the meal with one we hope suits your preferences better, and updates your preferences in our database. Meaning this meal won't be recommended again and will inform future recommendations.

Once you've OKAY'd the meal we'll format the meal plan into a pdf to download if you wish to view it offline. 

In additon, we'll generate a list of all recipes for you to use when you go shopping. This way there's no guessing and you can get all ingredients for the week at once easily!

## Updating Restrictions and Preferences
### Restrictions
If at any point you need to update your restictions just bavigate back to that page of the website form the homepage and resubmit the form with the new parameters.
This will update your data automatically.

### Preferences
After you have completed our initial preferences quiz you can go into our quiz to rate more recipes, but it's not necessary for getting recommendations.

Once you've successfully generated a mealplan the quiz contents will change slightly.
The meals we ask you to rate will be the same ones you were just recommended!

The purpose of this is to allow you to make the recipes we recommend and then rate them in our quiz, ensuring our recommendations get better over time as you try new things and we learn more about your preferences.

Enjoy!
