from flask import Flask, redirect
from flask_moment import Moment

ERROR_PAGE = 'error.html'
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


@app.errorhandler(404)
def error():
    """
    Error Page
    """
    return redirect(ERROR_PAGE), 404