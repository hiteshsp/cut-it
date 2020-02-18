from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL

#import re

#domain_regex= r'(^(https?://)w{3}.)?[a-zA-Z0-9][a-zA-Z0-9]+[a-zA-Z0-9].[a-zA-Z]{2,3}'
#pattern = re.compile(domain_regex)

class UrlForm(FlaskForm):
    long_url = StringField('URL',[DataRequired(),URL(message="Must be a valid URL with http:// or https://")])
    submit = SubmitField('Shorten iT!')
