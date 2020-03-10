import boto3
from botocore.exceptions import ClientError
from typing import Tuple
from url_shortener import app
from url_shortener.config import EXCEPTION_MESSAGE, URL_STORE


class DataStorage:
    def __init__(self):
        try:
            self.db_client = boto3.client('dynamodb')
        except ClientError as e:
            app.logger.error("Received error %s", e)

    def search_for_existing_short_url(self, long_url) -> Tuple[bool, str]:
        try:
            return self._search(long_url)
        except Exception as e:
            app.logger.debug(EXCEPTION_MESSAGE.format(e))

    def insert_new_short_url(self, long_url, short_url):
        try:
            return self._insert(long_url, short_url)
        except Exception as e:
            app.logger.debug(EXCEPTION_MESSAGE.format(e))

    def update_on_page_visit(self, long_url, short_url):
        try:
            return self._update(long_url, short_url)
        except Exception as e:
            app.logger.debug(EXCEPTION_MESSAGE.format(e))

    def get_short_url_statistics(self, short_url_identifier):
        try:
            return self._query(short_url_identifier)
        except Exception as e:
            app.logger(EXCEPTION_MESSAGE.format(e))

    def get_all_statistics(self):
        try:
            return self._scan()
        except Exception as e:
            app.logger.debug(EXCEPTION_MESSAGE.format(e))

    def _search(self, long_url):
        query_result = self.db_client.query(
            TableName=URL_STORE,
            ExpressionAttributeValues={
                ':url': {
                    'S': long_url,
                },
            },
            KeyConditionExpression='long_url = :url',
            ProjectionExpression='short_url_identifier'
        )
        if query_result['Count'] == 0:
            return False, "empty"

        existing_short_url_identifier = query_result['Items'][0]['short_url_identifier']['S']
        return True, existing_short_url_identifier

    def _insert(self, long_url, short_url):
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

    def _update(self, long_url, short_url):
        update_result = self.db_client.update_item(
            TableName=URL_STORE,
            Key={
                'long_url': {'S': long_url},
                'created_time': {'S': short_url.created_time}
            },
            UpdateExpression="set hits = :h, last_accessed_time = :la",
            ExpressionAttributeValues={
                ':h': {'N': short_url.hits},
                ':la': {'S': short_url.last_accessed_time}
            },
            ReturnValues="UPDATED_NEW")
        return update_result

    def _query(self, short_url_identifier):
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

    def _scan(self):
        scan_statistics_result = self.db_client.scan(
            TableName=URL_STORE,
            ProjectionExpression='long_url, short_url_identifier, last_accessed_time, hits',
        )
        return scan_statistics_result['Items']
