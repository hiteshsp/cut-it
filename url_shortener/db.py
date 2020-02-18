import boto3
import os
from time import time

client = boto3.client('dynamodb')
table_name = os.environ.get('TABLE_NAME')


class DynamoDB:

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
          Gets the stats
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