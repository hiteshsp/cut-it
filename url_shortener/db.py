import boto3
<<<<<<< Updated upstream
from botocore.exceptions import ClientError, ValidationError
from typing import Tuple
from url_shortener import app
from url_shortener.config import EXCEPTION_MESSAGE, URL_STORE


class DataStorage:
    def __init__(self):
        self.db_client = boto3.client('dynamodb')

    def search_for_existing_short_url(self, long_url) -> Tuple[bool, str]:
        try:
            return self._search(long_url)
        except ClientError as e:
            app.logger.error(EXCEPTION_MESSAGE.format(e))
        except Exception as e:
            app.logger.error(EXCEPTION_MESSAGE.format(e))

    def insert_new_short_url(self, long_url, short_url):
        try:
            return self._insert(long_url, short_url)
        except ClientError as e:
            app.logger.error(EXCEPTION_MESSAGE.format(e))
        except Exception as e:
            app.logger.error(EXCEPTION_MESSAGE.format(e))

    def update_on_page_visit(self, long_url, short_url):
        try:
            return self._update(long_url, short_url)
        except ClientError as e:
            app.logger.error(EXCEPTION_MESSAGE.format(e))
        except Exception as e:
            app.logger.error(EXCEPTION_MESSAGE.format(e))

    def get_short_url_statistics(self, short_url_identifier):
        try:
            return self._query(short_url_identifier)
        except ClientError as e:
            app.logger.error(EXCEPTION_MESSAGE.format(e))
        except Exception as e:
            app.logger.error(EXCEPTION_MESSAGE.format(e))

    def get_all_statistics(self):
        try:
            return self._scan()
        except ClientError as e:
            app.logger.error(EXCEPTION_MESSAGE.format(e))
        except Exception as e:
            app.logger.error(EXCEPTION_MESSAGE.format(e))

    def _search(self, long_url):
        try:
            query_result = self.db_client.query(
                TableName=URL_STORE,
=======
from url_shortener import app
from url_shortener.config import EXCEPTION_MESSAGE, URL_DETAILS

db_client = boto3.client('dynamodb')


class Persistence:
    def search(self, long_url):
        try:
            query_result = db_client.query(
                TableName=URL_DETAILS,
>>>>>>> Stashed changes
                ExpressionAttributeValues={
                    ':url': {
                        'S': long_url,
                    },
                },
                KeyConditionExpression='long_url = :url',
                ProjectionExpression='short_url_identifier'
            )
<<<<<<< Updated upstream
            if query_result['Count'] == 0:
                return False, "empty"

            existing_short_url_identifier = query_result['Items'][0]['short_url_identifier']['S']
            return True, existing_short_url_identifier
        except ValidationError as e:
            app.logger.error(EXCEPTION_MESSAGE.format(e))

    def _insert(self, long_url, short_url):
        try:
            insert_query_result = self.db_client.put_item(TableName=URL_STORE,
                                                          Item={
                                                              'long_url': {
                                                                  'S': long_url
                                                              },
                                                              'last_accessed_time': {
                                                                  'S': short_url.last_accessed_time
                                                              },
                                                              'short_url_identifier': {
                                                                  'S': short_url.identifier
                                                              },
                                                              'hits': {
                                                                  'N': short_url.hits
                                                              },
                                                              'created_time': {
                                                                  'S': short_url.created_time
                                                              },
                                                          })
            return insert_query_result
        except ValidationError as e:
            app.logger.error(EXCEPTION_MESSAGE.format(e))

    def _update(self, long_url, short_url):
        try:
            update_result = self.db_client.update_item(
                TableName=URL_STORE,
=======

            if query_result['Count'] == 0:
                return False, "empty"

            existing_short_url = query_result['Items'][0]['short_url']['S']
            return True, existing_short_url
        except Exception as ex:
            print(EXCEPTION_MESSAGE.format(ex))

    def insert(self, long_url, short_url):
        try:
            response = db_client.put_item(TableName=URL_DETAILS,
                                          Item={
                                              'long_url': {
                                                  'S': long_url
                                              },
                                              'last_accessed': {
                                                  'S': short_url.last_accessed
                                              },
                                              'short_url': {
                                                  'S': short_url.identifier
                                              },
                                              'hits': {
                                                  'N': short_url.hits
                                              },
                                              'created_time': {
                                                  'S': short_url.created_time
                                              },
                                          })
            return response
        except Exception as ex:
            app.logger.error(EXCEPTION_MESSAGE.format(ex))

    def update(self, long_url, short_url):
        try:
            update_result = db_client.update_item(
                TableName=URL_DETAILS,
>>>>>>> Stashed changes
                Key={
                    'long_url': {'S': long_url},
                    'created_time': {'S': short_url.created_time}
                },
                UpdateExpression="set hits = :h, last_accessed_time = :la",
                ExpressionAttributeValues={
                    ':h': {'N': short_url.hits},
<<<<<<< Updated upstream
                    ':la': {'S': short_url.last_accessed_time}
                },
                ReturnValues="UPDATED_NEW")
            return update_result
        except ValidationError as e:
            app.logger.error(EXCEPTION_MESSAGE.format(e))
=======
                    ':la': {'S': short_url.last_accessed}
                },
                ReturnValues="UPDATED_NEW")
            return update_result
        except Exception as e:
            app.logger.error(EXCEPTION_MESSAGE.format(e))


def get_short_url_statistics(short_url):
    try:
        response = db_client.query(
            TableName=URL_DETAILS,
            IndexName='short_url-index',
            ExpressionAttributeValues={':url': {
                'S': short_url,
            },
            },
            KeyConditionExpression='short_url = :url',
            ProjectionExpression='long_url, created_time, last_accessed, hits'

        )
        return response
    except Exception as ex:
        app.logger.error(EXCEPTION_MESSAGE.format(ex))
>>>>>>> Stashed changes

    def _query(self, short_url_identifier):
        try:
            query_statistics_result = self.db_client.query(
                TableName=URL_STORE,
                IndexName='short_url_identifier-index',
                ExpressionAttributeValues={':url': {
                    'S': short_url_identifier,
                },
                },
                KeyConditionExpression='short_url_identifier = :url',
                ProjectionExpression='long_url, created_time, last_accessed_time, hits'
            )
            return query_statistics_result
        except ValidationError as e:
            app.logger.error(EXCEPTION_MESSAGE.format(e))

<<<<<<< Updated upstream
    def _scan(self):
        try:
            scan_statistics_result = self.db_client.scan(
                TableName=URL_STORE,
                ProjectionExpression='long_url, short_url_identifier, last_accessed_time, hits',
            )
            return scan_statistics_result['Items']
        except ValidationError as e:
            app.logger.error(EXCEPTION_MESSAGE.format(e))
=======
def get_statistics():
    try:
        scan_result = db_client.scan(
            TableName=URL_DETAILS,
            ProjectionExpression='long_url, short_url, last_accessed, hits',
        )
        return scan_result['Items']
    except Exception as e:
        app.logger.error(EXCEPTION_MESSAGE.format(e))
>>>>>>> Stashed changes
