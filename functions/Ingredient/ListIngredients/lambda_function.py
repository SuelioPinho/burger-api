import boto3
import json

def lambda_handler(event, context):
    return {
        'bacon': 0,
        'cheese': 0,
        'meat': 0,
        'salad': 0
    }
