import boto3
import json
import uuid

def lambda_handler(event, context):
    order = event["body"]
    order["id"] = str(uuid.uuid4())
    order["sort_key"] = 'orders'

    params = {
        'method': 'create',
        'params': {
            'table': 'orders',
            'entity': order
        }
    }

    response = call_function("burger-api-dev", "GenericDao", params)
    return response

def call_function(Namespace, FunctionName, Params):
    callable_function = "{}-{}".format(Namespace, FunctionName)
    client = boto3.client('lambda')
    responseStream = client.invoke(FunctionName=callable_function, InvocationType='RequestResponse', Payload=json.dumps(Params))
    payload = responseStream['Payload']
    responseString = payload.read()
    response = json.loads(responseString)
    return response
