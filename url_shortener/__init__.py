import os
from flask import Flask, redirect
from flask_moment import Moment

app_configs = ['SECRET_KEY', 'IP', 'TABLE_NAME']
for app_config in app_configs:
    if os.environ.get(app_config) is None:
        raise KeyError(str(app_config) + ' is missing.')

app = Flask(__name__)
app.config.from_pyfile('config.py')
url_last_accessed = Moment(app)

from url_shortener import views
from url_shortener import db
from url_shortener import forms
