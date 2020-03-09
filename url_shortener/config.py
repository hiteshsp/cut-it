import os
from time import time

SECRET_KEY = os.environ.get("SECRET_KEY")
BASE_URL = os.environ.get('IP')
ERROR_PAGE = 'error.html'
HOME_PAGE = 'index.html'
URL_PAGE = 'success.html'
CURRENT_TIME = str(int(time()))
URL_DETAILS = os.environ.get('TABLE_NAME')
EXCEPTION_MESSAGE = 'Exception occurred, msg: {}'
