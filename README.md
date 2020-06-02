# Web50 2020 Project 3 - Pizza

In this project, I built a web application for handling a pizza restaurant’s online orders. Users are able to browse the restaurant’s menu, add items to their cart, and submit their orders. Customers can pay by card or cash and will recieve an order confirmation email. Meanwhile, the restaurant owners are able to add and update menu items, and view orders that have been placed. Restaurent owners can change the status of an order and customers will see the new status. This project uses a bootstrap theme from colorlib that I have customised.

## Root directory

- manage.py : A python script that can be used to perform useful operations on a web application.
- db.sqlite3 file: Main database file.
- .gitignore: Various files put into this so git can ignore them such as .env and database file.
- requirements: django, stripe and python-dotenv.

## Pizza folder

Project folder with key files:

- _init_.py: Defines the directory project-name as a Python ‘package’.
- settings.py: Basic settings, like time zone, other applications installed in the project, what sort of - database is used, etc.
- urls.py: Determines what URLs/routes can be accessed when using the web application
- wsgi.py: A file that helps to deploy an application to a web server.
- .env file: Holds all secret keys.

## Orders folder

This is the application folder. It includes migrations directory, static directory and templates directory.

- Migrations: Django automatically detects and changes to models.py and automatically generates the necessary SQL code to make the necessary changes. These are stored in this directory.
- Static: Contains all static files such as javascript, images, scss and css.
- Templates: Contains all html templates for the web app.
- app.py: Contains application config class.
- _init_.py: Defines the directory application-name as a Python ‘package’.

Other key files included in the orders folder is mentioned below.

## admin.py

I registerd all the models with Django Admin here and also created some ModelAdmin classes to customise how Admin presents data from database.

## forms.py

I have created form classes in django and used these in templates. Most of the forms are based on models so makes it easier to update the database.

## models.py

This is where I have defined all my models. This includes all models to do with the items on the menu, making online orders and a model to extend django's User model.

## signals.py

This file makes use of django's logged in and looged out signals to present custom messages.

## tokens.py

This file creates a custom token for account activiation (based on built-in password reset token). So customers recieve an email with the token and when they click on it, their account is activated and registration is completed.

## urls.py

This file contains all url routes for the views I have created.

## utils.py

This file contains custom functions created for views. This helps to keep the length of views.py minimal as possible.

## views.py

This file contains all view functions for each url route in the urls.py file.
