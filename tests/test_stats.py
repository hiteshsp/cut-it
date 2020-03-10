import unittest
from url_shortener import app
from tests.ignore_warnings import ignore_warnings


class StatsTest(unittest.TestCase):
    @ignore_warnings
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        self.app = app.test_client()
        self.assertEqual(app.debug, False)

    def tearDown(self):
        """ Nothing to clean up."""
        pass

    @ignore_warnings
    def test_stats_page(self):
        response = self.app.get('/stats', follow_redirects=True)
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
