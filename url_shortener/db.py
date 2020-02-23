import boto3
import os
from time import time
from url_shortener import app

# Boto Client to interact with the DynamoDB
client = boto3.client('dynamodb')
table_name = os.environ.get('TABLE_NAME')

# Constant for exception handling
EXCEPTION_MSG = 'Exception occurred, msg: {}'


class DynamoDB:
    """
        Creates an Database Object which includes helper functions like
        1. search : Finds the exisiting short_url from DB
        2. insert : Inserts items into DB
        3. update : Updates the records using short_url as hash key, it uses secondary index. 
    """

    def __init__(self, obj):
        """
            Constructor which accepts an 'obj' dict
        """
        self.obj = obj

    def search(self):
        """
           Searches for duplicates
           If found returns <'True', response object>
           else return 'False'
        """
        try:
            response = client.query(
                TableName=table_name,
                ExpressionAttributeValues={
                    ':url': {
                        'S': self.obj['long_url'],
                    },
                },
                KeyConditionExpression='long_url = :url',
                ProjectionExpression='short_url'
            )

            if response['Count'] == 0:
                return False, "empty"

            return True, response
        except Exception as ex:
            print(EXCEPTION_MSG.format(ex))

    def insert(self):
        """
        This method inserts items into the table
        """
        try:
            item = client.put_item(TableName=table_name,
                                   Item={
                                       'long_url': {
                                           'S': self.obj['long_url']
                                       },
                                       'last_accessed': {
                                           'S': self.obj['last_accessed']
                                       },
                                       'short_url': {
                                           'S': self.obj['short_url']
                                       },
                                       'hits': {
                                           'N': self.obj['hits']
                                       },
                                       'created_time': {
                                           'S': self.obj['created_time']
                                       },
                                   })
            return item
        except Exception as ex:
            app.logger.error(EXCEPTION_MSG.format(ex))

    def update(self):
        """
            Update a field of the table
        """
        try:
            response = client.update_item(
                TableName=table_name,
                Key={
                    'long_url': {'S': self.obj['long_url']},
                    'created_time': {'S': self.obj['created_time']}
                },
                UpdateExpression="set hits = :h, last_accessed = :la",
                ExpressionAttributeValues={
                    ':h': {'N': self.obj['hits']},
                    ':la': {'S': self.obj['last_accessed']}
                },
                ReturnValues="UPDATED_NEW")
            return response
        except Exception as ex:
            app.logger.error(EXCEPTION_MSG.format(ex))


def retrieve_stats(short_url):
    """
          Returns response which contains long_url, created_time, last_accessed, hits
    """
    try:
        response = client.query(
            TableName=table_name,
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
        app.logger.error(EXCEPTION_MSG.format(ex))


def scan():
    """
        Returns all records for stats page
    """
    try:
        response = client.scan(
            TableName=table_name,
            ProjectionExpression='long_url, short_url, last_accessed, hits',
        )
        return response
    except Exception as ex:
        app.logger.error(EXCEPTION_MSG.format(ex))
