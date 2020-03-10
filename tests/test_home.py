import unittest
from pynamodb.connection import TableConnection
from tests.ignore_warnings import ignore_warnings
from tests.utils import get_time
from url_shortener import app


class HomeTest(unittest.TestCase):
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
        self.app_context.pop()

    @ignore_warnings
    def test_home_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    @ignore_warnings
    def test_form_success(self):
        response = self.app.post(
            '/', data={'long_url': 'http://www.google.com', 'created_time': get_time()})
        self.assertEqual(response.status_code, 200)

    @ignore_warnings
    def test_form_failure(self):
        data = {'long_url': 'http://yahoo.com', 'created_time': get_time()}
        response = self.app.post(
            '/', data=data)
        self.assertEqual(response.status_code, 200)
        try:
            conn = TableConnection('cut-it-datastore', region='eu-north-1')
            conn.delete_item(data['long_url'], data['created_time'])
        except Exception as ex:
            app.logger.info("Exception in test_form_failure {}".format(ex))


if __name__ == "__main__":
    unittest.main()
