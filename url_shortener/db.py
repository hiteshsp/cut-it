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
                                   })
        except:
            print("Exception Occurred")


def retrieve_stats(short_url):
    """
          Returns response which contains long_url, short_url and visits
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
            ProjectionExpression='long_url'
        )
        return response
    except:
        print("Exception Occurred")
def scan():
    """
        Returns all records for stats page
    """
    try:
        response = client.scan(
            TableName=table_name,
            ProjectionExpression='long_url, short_url',
            )
        return response
    except:
        print("An exception in scan() method")