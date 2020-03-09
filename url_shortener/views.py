import random
import redis
import short_url
from dynamodb_json import json_util as json
from datetime import datetime
from flask import render_template, redirect
from time import time
from typing import Tuple
from url_shortener import app
from url_shortener.config import BASE_URL, CURRENT_TIME, ERROR_PAGE, EXCEPTION_MESSAGE, URL_PAGE, HOME_PAGE
from url_shortener.db import Persistence
from url_shortener.forms import URLForm


class ShortURL:
    identifier: str
    created_time: str
    last_accessed_time: str
    hits: str


@app.route('/', methods=['POST', 'GET'])
def shortener() -> None:
    try:
        url_form = URLForm()
        if url_form.validate_on_submit():
            long_url = url_form.long_url.data
            persister = Persistence()
            url_exists, short_url_identifier = _get_short_url_identifier(persister, long_url)
            if url_exists:
                app.logger.debug('Returning existing short url:' + short_url_identifier)
                return render_template(URL_PAGE,
                                       form=url_form,
                                       long_url=long_url,
                                       short_url=BASE_URL + short_url_identifier)
            else:
                error, short_url_identifier = _create_short_url(persister, long_url)
                if error is not None:
                    app.logger.error("{}".format(error))

                return render_template(URL_PAGE,
                                       form=url_form,
                                       long_url=long_url,
                                       short_url=BASE_URL + short_url_identifier)

        return render_template(HOME_PAGE, form=url_form)
    except Exception as e:
        app.logger.debug('index(): ' + EXCEPTION_MESSAGE.format(e))


def _get_short_url_identifier(persister, long_url) -> Tuple[bool, str]:
    url_exists, short_url_identifier = persister.search_for_existing_short_url(long_url)
    del persister
    return url_exists, short_url_identifier


def get_identifier_tracker():
    identifier_tracker = redis.Redis(host='localhost', port=6379)
    return identifier_tracker


def _create_short_url(persister, long_url):
    try:
        identifier_tracker = get_identifier_tracker()
        identifier = _get_unique_identifier(identifier_tracker)
        new_short_url = ShortURL()
        new_short_url.identifier = short_url.encode_url(identifier, min_length=6)
        new_short_url.created_time = CURRENT_TIME
        new_short_url.last_accessed_time = CURRENT_TIME
        new_short_url.hits = '0'
        persister.insert_new_short_url(long_url, new_short_url)
        del persister
        app.logger.debug('index(): Insertion Successful')
    except Exception as e:
        return e, ''
    return None, new_short_url.identifier


def _get_unique_identifier(identifier_tracker):
    try:
        existing_identifier = int(identifier_tracker.get('identifier'))
        unique_identifier = random.randrange(1, 1000, 1) if existing_identifier == 0 else existing_identifier + 1
        identifier_tracker.set('identifier', unique_identifier)
        return unique_identifier
    except Exception as e:
        app.logger.debug("{}".format(e))


@app.route("/stats")
def display_statistics() -> None:
    try:
        persister = Persistence()
        statistics = json.loads(persister.get_statistics())
        del persister
        if not statistics:
            return render_template(ERROR_PAGE)

        for short_url_statistics in statistics:
            short_url_statistics['last_accessed_time'] = datetime.utcfromtimestamp(
                int(short_url_statistics['last_accessed_time']))

        statistics = sorted(statistics, key=lambda url: short_url_statistics['hits'], reverse=True)
        app.logger.debug('statistics Object from scan() {}'.format(statistics))
        return render_template('stats.html', urls=statistics, domain=BASE_URL)
    except Exception as e:
        app.logger.debug("stats(): " + EXCEPTION_MESSAGE.format(e))


@app.route("/<path:short_url_identifier>", methods=['GET'])
def route_short_url(short_url_identifier) -> None:
    try:
        persister = Persistence()
        short_url_statistics = json.loads(persister.get_short_url_statistics(short_url_identifier))
        if short_url_statistics['Count'] == 0:
            return render_template(ERROR_PAGE)

        short_url_statistics = short_url_statistics['Items'][0]
        existing_short_url = ShortURL()
        existing_short_url.created_time = short_url_statistics['created_time']
        existing_short_url.last_accessed_time = str(int(time()))
        existing_short_url.hits = str(int(short_url_statistics['hits']) + 1)
        long_url = short_url_statistics['long_url']
        app.logger.debug(short_url_statistics)
        persister.update_on_page_visit(long_url, existing_short_url)
        del persister
        return redirect(long_url)
    except Exception as e:
        app.logger.debug('short_urls(): ' + EXCEPTION_MESSAGE.format(e))


@app.route("/<path:short_url_identifier>/stats")
def display_short_url_statistics(short_url_identifier) -> None:
    try:
        persister = Persistence()
        short_url_statistics = persister.get_short_url_statistics(short_url_identifier)
        del persister
        if short_url_statistics['Count'] == 0:
            return "<h1>Invalid Short URL</h1>"

        long_url = short_url_statistics['Items'][0]['long_url']['S']
        hits = short_url_statistics['Items'][0]['hits']['N']
        app.logger.debug('Short URL response : {}'.format(short_url_statistics))
        return render_template('short-stats.html',
                               long_url=long_url,
                               short_url=short_url_identifier,
                               domain=BASE_URL,
                               hits=hits)
    except Exception as e:
        app.logger.debug('get_stats(): ' + EXCEPTION_MESSAGE.format(e))


@app.errorhandler(404)
def page_not_found() -> None:
    return redirect(ERROR_PAGE), 404
