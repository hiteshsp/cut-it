from flask import Flask
from flask_moment import Moment

# '__name__' to refer the current file
app = Flask(__name__)

# Loading the variables from the config files
app.config.from_pyfile('config.py',)

# Setting the required variables for the application
app.config.get("SECRET_KEY")
moment = Moment(app)
from url_shortener import views
from url_shortener import db
from url_shortener import forms
