import redis
import short_url
from dynamodb_json import json_util as json
from datetime import datetime
from flask import render_template, redirect
from time import time
from typing import Tuple
from url_shortener import app
from url_shortener import config
from url_shortener.db import DataStorage
from url_shortener.forms import URLForm


class ShortURL:
    identifier: str
    created_time: str
    last_accessed_time: str
    hits: str


class DisplayShortURL:
    form: str
    long_url: str
    short_url_fqdn: str


@app.route('/', methods=['GET'])
def display_home_page():
    try:
        url_form = URLForm()
        return render_template(config.HOME_PAGE, form=url_form)
    except Exception as e:
        app.logger.debug(config.EXCEPTION_MESSAGE.format(e))


@app.route('/', methods=['POST'])
def shorten_the_url():
    url_form = URLForm()
    if url_form.validate_on_submit():
        long_url = url_form.long_url.data
        data_store = DataStorage()
        try:
            url_exists, short_url_identifier = _get_short_url_identifier(
                data_store, long_url)
        except Exception as e:
            app.logger.error(config.EXCEPTION_MESSAGE.format(e))
        display_short_url = DisplayShortURL()
        display_short_url.form = url_form
        display_short_url.long_url = long_url
        if url_exists:
            short_url_fqdn = config.BASE_URL + short_url_identifier
            display_short_url.short_url_fqdn = short_url_fqdn
            _render_short_url(display_short_url)

        else:
            try:
                error, short_url_identifier = _create_short_url(
                    data_store, long_url)
            except Exception as e:
                app.logger.error(config.EXCEPTION_MESSAGE.format(e))
            else:
                short_url_fqdn = config.BASE_URL + short_url_identifier
                if error is not None:
                    app.logger.error(config.EXCEPTION_MESSAGE.format(error))

                app.logger.debug("Generated Short URL: " + short_url_fqdn)
                _render_short_url(display_short_url)


def _render_short_url(display_short_url):
    return render_template(config.URL_PAGE,
                           form=display_short_url.form,
                           long_url=display_short_url.long_url,
                           short_url=display_short_url.short_url)


def _get_short_url_identifier(data_store, long_url) -> Tuple[bool, str]:
    url_exists, short_url_identifier = data_store.search_for_existing_short_url(
        long_url)
    del data_store
    return url_exists, short_url_identifier


def _get_identifier_tracker():
    host = config.REDIS_HOST
    port = config.REDIS_PORT
    try:
        identifier_tracker = redis.Redis(host=host, port=port)
        return identifier_tracker
    except ConnectionError as e:
        app.logger.error(config.EXCEPTION_MESSAGE.format(e))
    except Exception as e:
        app.logger.error(config.EXCEPTION_MESSAGE.format(e))


def _create_short_url(data_store, long_url):
    current_time = config.CURRENT_TIME
    identifier_tracker = _get_identifier_tracker()
    identifier = _get_unique_identifier(identifier_tracker)
    new_short_url = ShortURL()
    new_short_url.identifier = short_url.encode_url(
        identifier, min_length=6)
    new_short_url.created_time = current_time
    new_short_url.last_accessed_time = current_time
    new_short_url.hits = '0'
    data_store.insert_new_short_url(long_url, new_short_url)
    del data_store
    app.logger.debug('index(): Insertion Successful')
    return None, new_short_url.identifier


def _get_unique_identifier(identifier_tracker):
    existing_identifier = int(identifier_tracker.get('identifier'))
    unique_identifier = existing_identifier + 1
    identifier_tracker.set('identifier', unique_identifier)
    return unique_identifier


@app.route("/stats")
def display_statistics() -> None:
    data_store = DataStorage()
    statistics = json.loads(data_store.get_all_statistics())
    del data_store
    if not statistics:
        return render_template(config.ERROR_PAGE)

    for short_url_statistics in statistics:
        short_url_statistics['last_accessed_time'] = datetime.utcfromtimestamp(
            int(short_url_statistics['last_accessed_time']))

    statistics = sorted(statistics, key=lambda url: short_url_statistics['hits'], reverse=True)
    app.logger.debug('statistics Object from scan() {}'.format(statistics))
    return render_template('stats.html', urls=statistics, domain=config.BASE_URL)


@app.route("/<path:short_url_identifier>", methods=['GET'])
def route_short_url(short_url_identifier) -> None:
    data_store = DataStorage()
    short_url_statistics = json.loads(
        data_store.get_short_url_statistics(short_url_identifier))
    if short_url_statistics['Count'] == 0:
        return render_template(config.ERROR_PAGE)

    short_url_statistics = short_url_statistics['Items'][0]
    existing_short_url = ShortURL()
    existing_short_url.created_time = short_url_statistics['created_time']
    existing_short_url.last_accessed_time = str(int(time()))
    existing_short_url.hits = str(int(short_url_statistics['hits']) + 1)
    long_url = short_url_statistics['long_url']
    app.logger.debug(short_url_statistics)
    data_store.update_on_page_visit(long_url, existing_short_url)
    del data_store
    return redirect(long_url)


@app.route("/<path:short_url_identifier>/stats")
def display_short_url_statistics(short_url_identifier) -> None:
    data_store = DataStorage()
    short_url_statistics = json.loads(data_store.get_short_url_statistics(
        short_url_identifier))
    del data_store
    if short_url_statistics['Count'] == 0:
        return "<h1>Invalid Short URL</h1>"

    short_url_statistics = short_url_statistics['Items'][0]
    long_url = short_url_statistics['long_url']
    hits = short_url_statistics['hits']
    app.logger.debug(
        'Short URL response : {}'.format(short_url_statistics))
    return render_template('short-stats.html',
                           long_url=long_url,
                           short_url=short_url_identifier,
                           domain=config.BASE_URL,
                           hits=hits)


@app.errorhandler(404)
def page_not_found(error) -> None:
    return redirect(config.ERROR_PAGE), 404
