import unittest
from url_shortener import app
from tests.ignore_warnings import ignore_warnings
from werkzeug import exceptions


class ExceptionsTest(unittest.TestCase):
    @ignore_warnings
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        self.app = app.test_client()
        self.assertEqual(app.debug, False)

    @ignore_warnings
    def tearDown(self):
        """ Nothing to clean up."""
        pass

    @ignore_warnings
    def test_home_exception(self):
        self.app.get('/', follow_redirects=False)
        self.assertRaises(exceptions.InternalServerError)

    @ignore_warnings
    def test_stats_page(self):
        self.app.get('/stats', follow_redirects=True)
        self.assertRaises(exceptions.InternalServerError)


if __name__ == "__main__":
     unittest.main()
