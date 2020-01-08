import boto3
import json

def call_function(Namespace, FunctionName, Params):
    callable_function = "{}-{}".format(Namespace, FunctionName)
    client = boto3.client('lambda')
    responseStream = client.invoke(FunctionName=callable_function, InvocationType='RequestResponse', Payload=json.dumps(Params))
    payload = responseStream['Payload']
    responseString = payload.read()
    response = json.loads(responseString)
    return response
