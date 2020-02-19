from url_shortener import app
from flask import render_template, url_for, redirect, request
from url_shortener.forms import UrlForm
from url_shortener.db import DynamoDB, retrieve_stats, scan
import short_url
from time import time
import random
import os
from flask.helpers import flash

#empty dictionary for the inserting form object to db
obj = {}

#prefix domain
domain = os.environ.get('IP')  # get the public IP


@app.route('/', methods=['POST', 'GET'])
def index():
    """
        This method renders the home page of the app.
    """
    try:
        new_form = UrlForm()
        if new_form.validate_on_submit():
            obj['long_url'] = new_form.long_url.data
            obj['timestamp'] = str(int(time()))
            obj['short_url'] = short_url.encode_url(random.randrange(1, 1000, 1))
            #obj['short_url'] = short_url.encode_url(random.randrange(1,1000,1)) need to think

            db_obj = DynamoDB(obj)
            flag, response = db_obj.search()
            if flag == True:
                response = response['Items'][0]['short_url']['S']
                print(response)  # debug point
                return render_template('index.html', form=new_form, long_url=obj['long_url'], short_url=response)
            else:
                db_obj.insert()
                print("insert successful")  # debug point
                return render_template('index.html', form=new_form, long_url=obj['long_url'], short_url=domain+obj['short_url'])
        return render_template('index.html', form=new_form)
    except:
        print("Exception Occured")

@app.route("/stats")
def stats():
    """
        This method is used to display the statistics of the 'active' shortened URL's
    """
    #TODO
    response = scan()
    if response['Count'] == 0:
        return render_template('error.html')
    response = response['Items']
    return render_template('stats.html',url=response)

@app.route("/<path:url>", methods=['GET'])
def short_urls(url):
    """
        Paths to shorturls
    """
    response = retrieve_stats(url)
    if response['Count'] == 0:
        return render_template('error.html')
    response = response['Items'][0]['long_url']['S']
    return redirect(response)

@app.route("/<path:short_url>/stats")
def get_stats(short_url):
    """
        Renders Stats per ShortURL
    """
    #TODO
    return render_template('stats.html')

@app.errorhandler(404)
def error():
    """
    Error Page
    """
    return redirect('error.html'), 404