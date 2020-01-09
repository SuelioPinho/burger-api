import boto3
import json
import uuid
import decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)

def lambda_handler(event, context):
    order = event["body"]
    order["id"] = str(uuid.uuid4())
    order["sort_key"] = 'orders'
    order["price"] = json.dumps(decimal.Decimal(order["price"]), cls=DecimalEncoder)

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
