import unittest
from url_shortener import app
from url_shortener.db import DynamoDB
from pynamodb.connection import TableConnection
from time import time
from url_shortener.tests.ignore_warnings import ignore_warnings
import short_url
from werkzeug import exceptions

CURRENT_TIME = str(int(time()))

obj = dict()


class ShortURLTest(unittest.TestCase):
    """
        Contains unit tests for stats
    """
    @ignore_warnings
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        self.app = app.test_client()
        self.assertEqual(app.debug, False)

        obj['long_url'] = "http://abc.xyz"
        obj['created_time'] = CURRENT_TIME
        obj['short_url'] = short_url.encode_url(1, min_length=6)
        obj['hits'] = '0'
        obj['last_accessed'] = CURRENT_TIME
        db = DynamoDB(obj)
        db.insert()

    @ignore_warnings
    def tearDown(self):
        """
            Post tests cleanup code    
        """
        conn = TableConnection('flask-datastore', region='eu-north-1')
        conn.delete_item(obj['long_url'], obj['created_time'])

    @ignore_warnings
    def test_short_url(self):
        """
           Tests for successful rendering of /<short_url>
        """
        response = self.app.get('/'+obj['short_url'], follow_redirects=False)
        self.assertEqual(response.status_code, 302)

    @ignore_warnings
    def test_stats_page(self):
        """
           Tests for successful rendering of /<short_url>/stats page 
        """
        response = self.app.get('/'+obj['short_url']+'/stats', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertRaises(exceptions.InternalServerError)


if __name__ == "__main__":
     unittest.main()
