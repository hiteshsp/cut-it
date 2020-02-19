import boto3
import os
from time import time

# Boto Client to interact with the DynamoDB
client = boto3.client('dynamodb')
table_name = os.environ.get('TABLE_NAME')


class DynamoDB:
    """
        Creates an Database Object which includes helper functions like
        1. search : Finds the exisiting short_url from DB
        2. insert : Inserts items into DB
    """

    def __init__(self, obj):
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
                ExpressionAttributeValues={':url': {
                    'S': self.obj['long_url'],
                },
                },
                KeyConditionExpression='long_url = :url',
                ProjectionExpression='short_url'
            )

            if response['Count'] == 0:
                return False, "empty"

            return True, response
        except:
            print("An Exception Occ")

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
                                       'timestamp': {
                                           'S': self.obj['timestamp']
                                       },
                                       'short_url': {
                                           'S': self.obj['short_url']
                                       },
                                       'hits': {
                                           'N': self.obj['hits']
                                       },
                                   })
            return item
        except:
            print("Exception Occurred in insert()\n")

    def update(self):
        """
            Update a field of the table
        """
        try:
            response = client.update_item(
                TableName=table_name,
                Key={
                    'long_url': {'S': self.obj['long_url']},
                    'timestamp': {'S': self.obj['timestamp']}
                },
                UpdateExpression="set hits = :h",
                ExpressionAttributeValues={
                    ':h': {'N': self.obj['hits']}
                },
                ReturnValues="UPDATED_NEW")
            return response
        except:
            print("Exception Occurred in update()")


def retrieve_stats(short_url):
    """
          Returns response which contains long_url and hits
    """
    try:
        response = client.query(
            TableName=table_name,
            IndexName='short_url-index',
            ExpressionAttributeValues={':url': {
                'S': short_url,
            },
            },
            ExpressionAttributeNames={'#timestamp': 'timestamp'},
            KeyConditionExpression='short_url = :url',
            ProjectionExpression='long_url, #timestamp, hits',
        )
        return response
    except:
        print("Exception Occurred retrieve_stats()")


def scan():
    """
        Returns all records for stats page
    """
    try:
        response = client.scan(
            TableName=table_name,
            ProjectionExpression='long_url, short_url, hits',
        )
        return response
    except:
        print("An exception in scan() method")