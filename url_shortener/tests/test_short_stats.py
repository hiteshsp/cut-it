import unittest
from url_shortener import app
from url_shortener.db import DynamoDB

import time

TIME = str(time.time())
# object to insert the dummy record
obj = {}

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
        
        obj['long_url']='http://www.google.com'
        obj['created_time']= TIME
        obj['short_url']='asdf'
        obj['hits']='10'

        self.obj = obj
        try:
            db = DynamoDB(obj)        
            db.insert()
        except Exception as ex:
               print('Exception occurred {}'.format(ex))  
                
    def tearDown(self):
        # pass the test once test is complete
        db = DynamoDB(self.obj)
        db.delete()

    def test_stats_page(self):
        response = self.app.get('/'+ self.obj['short_url'] +'/stats', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()
    