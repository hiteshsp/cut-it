import unittest
from url_shortener import app


class StatsTest(unittest.TestCase):
    """
        Contains unit tests for stats
    """
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        self.app = app.test_client()
        self.assertEqual(app.debug, False)


    def tearDown(self):
        # pass the test once test is complete
        pass

    def test_stats_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()
    