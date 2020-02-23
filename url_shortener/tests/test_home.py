import unittest
from url_shortener import app
from url_shortener.tests.ignore_warnings import ignore_warnings
from pynamodb.connection import TableConnection
from time import time

TIME = str(int(time()))


class HomeTest(unittest.TestCase):
    """
        Contains unit tests for stats
    """
    @ignore_warnings
    def setUp(self):

        self.app_context = app.app_context()
        self.app_context.push()
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        self.app = app.test_client()
        self.assertEqual(app.debug, False)
        app.app_context()

    def tearDown(self):
        # pass the test once test is complete
        self.app_context.pop()

    @ignore_warnings
    def test_home_page(self):
        """
            Test Case for page load
        """
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    @ignore_warnings
    def test_form_success(self):
        """
            Test Case for form existing URL's
        """
        response = self.app.post(
            '/', data={'long_url': 'http://www.google.com', 'created_time': TIME})
        self.assertEqual(response.status_code, 200)

    @ignore_warnings
    def test_form_failure(self):
        """
            Test Case for New URL's
        """
        data={'long_url': 'http://yahoo.com', 'created_time': TIME}
        response = self.app.post(
            '/', data=data)
        self.assertEqual(response.status_code, 200)
        try:
            conn = TableConnection('flask-datastore', region='eu-north-1')
            conn.delete_item(data['long_url'], data['created_time'])
        except Exception as ex:
               app.logger.info("Exception in test_form_failure {}".format(ex))


if __name__ == "__main__":
    unittest.main()
