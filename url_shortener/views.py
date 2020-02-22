from url_shortener import app
from flask import render_template, url_for, redirect, request
from url_shortener.forms import UrlForm
from url_shortener.db import DynamoDB, retrieve_stats, scan
import short_url
from time import time
import random
import os
from flask.helpers import flash
from dynamodb_json import json_util as json
from datetime import datetime


#prefix domain
domain = os.environ.get('IP')  # get the public IP


HOME = 'index.html'
SUCCESS = 'success.html'
ERROR_PAGE = 'error.html'
CURRENT_TIME = str(int(time()))

#Constant for exception handling
EXCEPTION_MSG = 'Exception occurred, msg: {}'


@app.route('/', methods=['POST', 'GET'])
def index():
    """
        This method renders the HOME page of the app.
    """
    try:
        form = UrlForm()
        if form.validate_on_submit():
            #empty dictionary for the inserting form object to db
            obj = {}
            obj['long_url'] = form.long_url.data

            db_obj = DynamoDB(obj)
            flag, response = db_obj.search()
            if flag == True:
                response = response['Items'][0]['short_url']['S']
                return render_template(SUCCESS, form=form, long_url=obj['long_url'], short_url=domain+response)
            else:
                obj['short_url'] = short_url.encode_url(random.randrange(1, 1000, 1))
                obj['created_time'] = CURRENT_TIME
                obj['last_accessed'] = CURRENT_TIME
                obj['hits'] = '0'

                db_obj.insert()
                print("insert successful")
                return render_template(SUCCESS, form=form, long_url=obj['long_url'], short_url=domain+obj['short_url'])
        return render_template(HOME, form=form)
    except Exception as ex:
        print('index(): '+EXCEPTION_MSG.format(ex))



@app.route("/stats")
def stats():
    """
        This method is used to display the statistics of the shortened URL's
    """
    try:
        response = scan()
        if response['Count'] == 0:
            return render_template(ERROR_PAGE)
        response = response['Items']
        response = json.loads(response)
        
        # TODO: Change timestamp from string to int
        for obj in response:
          obj['last_accessed'] = datetime.utcfromtimestamp(int(obj['last_accessed']))
    
        response = sorted(response, key=lambda obj: obj['hits'], reverse=True)
        return render_template('stats.html', url=response, domain=domain)
    except Exception as ex:
        print("stats(): "+EXCEPTION_MSG.format(ex))


@app.route("/<path:url>", methods=['GET'])
def short_urls(url):
    """
        Paths to shorturls
    """
    try:
        response = retrieve_stats(url)
        if response['Count'] == 0:
            return render_template(ERROR_PAGE)
        
        obj = {}
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
    except Exception as ex:
        print('short_urls(): '+EXCEPTION_MSG.format(ex))


@app.route("/<path:url>/stats")
def get_stats(url):
    """
        Renders Stats per ShortURL
    """
    # Retrieving the given short url's stats from the table
    try:
        response = retrieve_stats(url)

        # If the response is zero.
        if response['Count'] == 0:
            return "Invalid Short URL"

        long_url = response['Items'][0]['long_url']['S']
        hits = response['Items'][0]['hits']['N']

        return render_template('short-stats.html', long_url=long_url, short_url=url, hits=hits)
    except Exception as ex:
        print('get_stats(): '+EXCEPTION_MSG.format(ex))


@app.errorhandler(404)
def error():
    """
    Error Page
    """
    return redirect(ERROR_PAGE), 404
