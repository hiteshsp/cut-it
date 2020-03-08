from flask import Flask, redirect
from flask_moment import Moment

app = Flask(__name__)
app.config.from_pyfile('config.py')
app.config.get('SECRET_KEY')
url_last_accessed = Moment(app)

from url_shortener import views
from url_shortener import db
from url_shortener import forms
