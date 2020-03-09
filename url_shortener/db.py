import boto3
from typing import Tuple
from url_shortener import app
from url_shortener.config import EXCEPTION_MESSAGE, URL_DETAILS


class Persistence:
    def __init__(self):
        self.db_client = boto3.client('dynamodb')

    def search_for_existing_short_url(self, long_url) -> Tuple[bool, str]:
        try:
            query_result = self.db_client.query(
                TableName=URL_DETAILS,
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
        except Exception as ex:
            app.logger.debug(EXCEPTION_MESSAGE.format(ex))

    def insert_new_short_url(self, long_url, short_url):
        try:
            insert_query_result = self.db_client.put_item(TableName=URL_DETAILS,
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
        except Exception as ex:
            app.logger.error(EXCEPTION_MESSAGE.format(ex))

    def update_on_page_visit(self, long_url, short_url):
        try:
            update_result = self.db_client.update_item(
                TableName=URL_DETAILS,
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
        except Exception as e:
            app.logger.error(EXCEPTION_MESSAGE.format(e))

    def get_short_url_statistics(self, short_url_identifier):
        try:
            query_statistics_result = self.db_client.query(
                TableName=URL_DETAILS,
                IndexName='short_url_identifier-index',
                ExpressionAttributeValues={':url': {
                    'S': short_url_identifier,
                },
                },
                KeyConditionExpression='short_url_identifier = :url',
                ProjectionExpression='long_url, created_time, last_accessed_time, hits'

            )
            return query_statistics_result
        except Exception as ex:
            app.logger.error(EXCEPTION_MESSAGE.format(ex))

    def get_statistics(self):
        try:
            scan_statistics_result = self.db_client.scan(
                TableName=URL_DETAILS,
                ProjectionExpression='long_url, short_url_identifier, last_accessed_time, hits',
            )
            return scan_statistics_result['Items']
        except Exception as e:
            app.logger.error(EXCEPTION_MESSAGE.format(e))
