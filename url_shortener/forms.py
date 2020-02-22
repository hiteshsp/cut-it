from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL


class UrlForm(FlaskForm):
    """
        Creates two elements for the long_url and a submit button
    """
    long_url = StringField('URL', [DataRequired(), URL(
        message="Must be a valid URL with http:// or https://")])
    submit = SubmitField('Shorten iT!')
