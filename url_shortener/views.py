from url_shortener import app
from flask import render_template, url_for, redirect, request
from url_shortener.forms import UrlForm
from url_shortener.db import DynamoDB
import short_url
from time import time
import random 

#empty dictionary for the inserting form object to db
obj={}

#prefix domain
domain='https://cut.it/'

@app.route('/', methods=['POST','GET'])
def index():
    """
        This method renders the home page of the app.
    """
    new_form = UrlForm()
    if new_form.validate_on_submit():
        obj['long_url'] = new_form.long_url.data
        obj['timestamp'] = str(int(time()))
        obj['short_url'] = domain + short_url.encode_url(random.randrange(1,1000,1))        
        #obj['short_url'] = short_url.encode_url(random.randrange(1,1000,1)) need to think

        db_obj = DynamoDB(obj)
        flag, response = db_obj.search()
        if flag == True:
            response = response['Items'][0]['short_url']['S'] 
            print(response) # debug point
            return render_template('index.html', form=new_form, short_url=response)            
        else:
            db_obj.insert()            
            print("insert successful") # debug point
            return render_template('index.html', form=new_form, short_url=obj['short_url'])
        
    return render_template('index.html', form=new_form)

@app.route("/stats")
def stats():
    """
        This method is used to display the statistics of the 'active' shortened URL's
    """
    return render_template('stats.html')

@app.route("/<path:short_url>/stats")
def get_stats(short_url):
    """
        Renders Stats per ShortURL
    """
    return render_template('short-stats.html')