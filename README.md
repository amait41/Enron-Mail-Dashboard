# Enron Mail Dashboard

![Argon Dashboard Django - Admin Dashboard coded in Django.](https://github.com/Maxime-LP/Employees-mails/blob/main/img_readme/preview.gif)


# Table of Contents

* [User guide](#user-guide)
* [Documentation](#documentation)

# User guide

## Quick start

Download the data at the following link: 

> UNZIP the sources or clone the private repository. After getting the code, open a terminal and navigate to the working directory, with product source code.

```bash
$ # Get the code
$ git clone https://github.com/Maxime-LP/Enron-Mail-Dashboard.git
$ cd Enron-Mail-Dashboard
$
$ # Virtualenv modules installation (Unix based systems)
$ virtualenv env
$ source env/bin/activate
$
$ # Virtualenv modules installation (Windows based systems)
$ # virtualenv env
$ # .\env\Scripts\activate
$
$ # Install modules - SQLite Storage
$ pip3 install -r requirements.txt
$
$ # Create tables
$ python manage.py makemigrations
$ python manage.py migrate
$
$ # Init Database 
$ ./insert.py # Enter 1 three times, like as follows:
$ #Preprocess XML file (0/1)? 1
$ #Create pickle file (0/1)? 1
$ #Update database (0/1)? 1
$
$ # Start the application
$ python manage.py runserver # default port 8000
$
$ # Or start the app with custom port
$ # python manage.py runserver 0.0.0.0:<your_port>
$
$ # Access the web app in browser: http://127.0.0.1:8000/ or http://localhost:7000/
```

> Note: To use the app, please access the registration page and create a new user. After authentication, the app will unlock the private pages.

The next time you use it, everything will be ready and you just need to connect to the web app.

## Preview page

| Dashboard Page | Employees Page | Couples Page  | Days Page | Profile Page | Login Page | Register Page  |
| --- | --- | ---  | --- | --- | ---  | ---  |
| ![Dashboard Page](https://github.com/Maxime-LP/Employees-mails/blob/main/img_readme/Home.png) | ![Employees Page](https://github.com/Maxime-LP/Employees-mails/blob/main/img_readme/Employees.png) | ![Couples Page](https://github.com/Maxime-LP/Employees-mails/blob/main/img_readme/Couples.png) | ![Days Page](https://github.com/Maxime-LP/Employees-mails/blob/main/img_readme/Days.png) | ![Profile Page](https://github.com/Maxime-LP/Employees-mails/blob/main/img_readme/Profile.png) | ![Login Page](https://github.com/Maxime-LP/Employees-mails/blob/main/img_readme/Login.png) | ![Register Page](https://github.com/Maxime-LP/Employees-mails/blob/main/img_readme/Register.png)

## Settings
- Employees Page: Period, number of results, low and high thresholds.
- Couple Page: Same as the Employees page.
- Days Page: Period, number of results, minimum number of emails per days.
- Profile Page: Enter the name of an Enron employee. 


# Documentation

The project was developed from the [Argon](https://github.com/creativetimofficial/vue-argon-dashboard) template. Thus, it is a web application using Django technology.
For the installation please refer to the [Quick Start](#quick-start) section.

## File Structure
Within the download you'll find the following directories and files:
```bash
< PROJECT ROOT >
   |
   |-- core/                               # Implements app logic and serve the static assets
   |    |-- settings.py                    # Django app bootstrapper
   |    |-- wsgi.py                        # Start the app in production
   |    |-- urls.py                        # Define URLs served by all apps/nodes
   |    |
   |    |-- static/
   |    |    |-- <css, JS, images>         # CSS files, Javascripts files
   |    |
   |    |-- templates/                     # Templates used to render pages
   |         |
   |         |-- includes/                 # HTML chunks and components
   |         |    |-- navigation.html      # Top menu component
   |         |    |-- sidebar.html         # Sidebar component
   |         |    |-- footer.html          # App Footer
   |         |    |-- scripts.html         # Scripts common to all pages
   |         |
   |         |-- layouts/                  # Master pages
   |         |    |-- base-fullscreen.html # Used by Authentication pages
   |         |    |-- base.html            # Used by common pages
   |         |
   |         |-- accounts/                 # Authentication pages
   |         |    |-- login.html           # Login page
   |         |    |-- register.html        # Register page
   |         |
   |      index.html                       # The default page
   |     page-404.html                     # Error 404 page
   |     page-500.html                     # Error 404 page
   |       *.html                          # All other HTML pages
   |
   |-- authentication/                     # Handles auth routes (login and register)
   |    |
   |    |-- urls.py                        # Define authentication routes  
   |    |-- views.py                       # Handles login and registration  
   |    |-- forms.py                       # Define auth forms  
   |
   |-- app/                                # A simple app that serve HTML files
   |    |
   |    |-- views.py                       # Serve HTML pages for authenticated users
   |    |-- urls.py                        # Define some super simple routes  
   |
   |-- requirements.txt                    # Development modules - SQLite storage
   |
   |-- .env                                # Inject Configuration via Environment
   |-- manage.py                           # Start the app - Django default start script
   |
   |-- employees_enron.xml                 # First file to process to populate the database
   |-- headers.pkl                         # Must be created after running the insert.py script
   |
   |-- ************************************************************************
```
## Application Settings

The main parameters of the application can be modified in the settings.py file in the root of the project.
In particular, the following settings are required to use a Postgres database:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # we use the postgresql adapter
        'NAME': 'database_name',
        'USER': 'my_username',
        'PASSWORD': 'my_password',
        'HOST': 'host_name',
        'PORT': '5432',
        'OPTIONS': {
            'options': '-c search_path='name_of_my_schema'
          },
        }
    }
```

To make it simpler, you can use a SQLite database:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME'  : 'db.sqlite3',
      }
   }
```
You can find the models of the applications in *authentication/models.py* and *app/models.py*. The database schema of application *app* is as follows:

![Schema BDD](https://github.com/Maxime-LP/Employees-mails/blob/main/img_readme/bdd_model.png)

## Views and URLs

To manage the views you have to modify the *views.py* files located in the directories *app* and *authentication*.
And to manage the redirection, it happens in the *urls.py* files in the *core*, *authentication* and *app* directories.

The templates are in the core directory and not in the applications directories:
- core/include for basic templates.
- core/layout for application *authentication*'s templates.
- core/\*.html for application *app*'s templates.
