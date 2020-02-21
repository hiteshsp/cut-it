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

home = 'index.html'
error_page = 'error.html'
current_time = str(int(time()))

@app.route('/', methods=['POST', 'GET'])
def index():
    """
        This method renders the home page of the app.
    """
    try:
        new_form = UrlForm()
        if new_form.validate_on_submit():
            obj['long_url'] = new_form.long_url.data
            obj['created_time'] = current_time
            obj['last_accessed'] = current_time
            obj['short_url'] = short_url.encode_url(
                random.randrange(1, 1000, 1))
            obj['hits'] = '0'
            
            db_obj = DynamoDB(obj)
            flag, response = db_obj.search()
            if flag == True:
                response = response['Items'][0]['short_url']['S']
                print(response)  # debug point
                return render_template(home, form=new_form, long_url=obj['long_url'], short_url=domain+response)
            else:
                db_obj.insert()
                print("insert successful")  # debug point
                return render_template(home, form=new_form, long_url=obj['long_url'], short_url=domain+obj['short_url'])
        return render_template(home, form=new_form)
    except:
        print("Exception Occured")


@app.route("/stats")
def stats():
    """
        This method is used to display the statistics of the 'active' shortened URL's
    """
    response = scan()
    if response['Count'] == 0:
        return render_template(error_page)
    response = response['Items']
    return render_template('stats.html', url=response)


@app.route("/<path:url>", methods=['GET'])
def short_urls(url):
    """
        Paths to shorturls
    """
    response = retrieve_stats(url)
    if response['Count'] == 0:
        return render_template(error_page)

    # long_url and created_time are key attributes
    # They are needed to update the hits and last_access time
    obj['long_url'] = response['Items'][0]['long_url']['S']
    obj['created_time'] = response['Items'][0]['created_time']['S']

    # Capturing the hits and last_accessed time for the update
    obj['last_accessed'] = str(int(time()))
    obj['hits'] = str(int(response['Items'][0]['hits']['N']) + 1)

    db = DynamoDB(obj)
    db.update()
    return redirect(obj['long_url'])


@app.route("/<path:url>/stats")
def get_stats(url):
    """
        Renders Stats per ShortURL
    """
    # Retrieving the given short url's stats from the table
    response = retrieve_stats(url)

    # If the response is zero.
    if response['Count'] == 0:
        return "Invalid Short URL"
        
    long_url = response['Items'][0]['long_url']['S']
    hits = response['Items'][0]['hits']['N']

    return render_template('short-stats.html', long_url=long_url, short_url=url, hits=hits)


@app.errorhandler(404)
def error():
    """
    Error Page
    """
    return redirect(error_page), 404
