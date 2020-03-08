import boto3
from url_shortener import app
from url_shortener.config import EXCEPTION_MESSAGE, URL_DETAILS

db_client = boto3.client('dynamodb')


class Persistence:
    def search(self, long_url):
        try:
            query_result = db_client.query(
                TableName=URL_DETAILS,
                ExpressionAttributeValues={
                    ':url': {
                        'S': long_url,
                    },
                },
                KeyConditionExpression='long_url = :url',
                ProjectionExpression='short_url'
            )

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
                Key={
                    'long_url': {'S': long_url},
                    'created_time': {'S': short_url.created_time}
                },
                UpdateExpression="set hits = :h, last_accessed = :la",
                ExpressionAttributeValues={
                    ':h': {'N': short_url.hits},
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


def get_statistics():
    try:
        scan_result = db_client.scan(
            TableName=URL_DETAILS,
            ProjectionExpression='long_url, short_url, last_accessed, hits',
        )
        return scan_result['Items']
    except Exception as e:
        app.logger.error(EXCEPTION_MESSAGE.format(e))
