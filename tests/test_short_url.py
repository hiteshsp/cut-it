import unittest
from pynamodb.connection import TableConnection
import short_url
from werkzeug import exceptions

from tests.utils import get_time
from url_shortener import app
from url_shortener.views import ShortURL
from url_shortener.db import Persistence
from tests.ignore_warnings import ignore_warnings

test_long_url = "http://abc.xyz"
test_short_url = ShortURL()

class ShortURLTest(unittest.TestCase):
    @ignore_warnings
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        self.app = app.test_client()
        self.assertEqual(app.debug, False)        
        test_short_url.created_time = get_time()
        test_short_url.identifier = short_url.encode_url(1, min_length=6)
        test_short_url.hits = '0'
        test_short_url.last_accessed_time = get_time()
        test_persister = Persistence()
        test_persister.insert_new_short_url(test_long_url, test_short_url)

    @ignore_warnings
    def tearDown(self):
        conn = TableConnection('cut-it-datastore', region='eu-north-1')
        conn.delete_item(test_long_url, test_short_url.created_time)

    @ignore_warnings
    def test_short_url(self):
        response = self.app.get('/'+ test_short_url.identifier, follow_redirects=False)
        self.assertEqual(response.status_code, 302)

    @ignore_warnings
    def test_stats_page(self):
        response = self.app.get('/'+ test_short_url.identifier+'/stats', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertRaises(exceptions.InternalServerError)


if __name__ == "__main__":
     unittest.main()
