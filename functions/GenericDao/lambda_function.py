import json
import boto3
import os
from boto3.dynamodb.conditions import Key, Attr
import unidecode

index = 'EntityIndex'

def lambda_handler(event, context):
	# Validate lambda parameters
	invalid = validate_requirements(event)
	if invalid != None:
		return invalid
	method = event['method']
	params = event['params']
	table = params['table']

	dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

	resource_table = dynamodb.Table('burger_table')

	result = None

	if method == 'list':
		if not "sort_key" in params:
			return { 'statusCode': 504, 'msg': 'Parametro <sort_key> nao especificado' }
		try:
			result = list(resource_table, params)
		except Exception as e:
			print(e)
			return { 'statusCode': 504, 'msg': 'Erro ao realizar consulta no banco de dados' }
		return { 'statusCode': 200, 'data': result }

	if method == 'get':
		columns = None
		if "columns" in params:
			columns = params['columns']
		if not "id" in params:
			return { 'statusCode': 503, 'msg': 'Parametro <id> nao especificado' }
		id_formated = "{}#{}".format(table, params['id'])
		try:
			if columns != None:
				response = resource_table.get_item(Key={'id':id_formated}, AttributesToGet=columns)
				result = unformat_empresa_id(table, response['Item'])
			else:
				response = resource_table.get_item(Key={'id':id_formated})
				if not "Item" in response:
					return { 'statusCode': 404, 'msg': 'Dado não encontrado' }
				result = unformat_empresa_id(table, response['Item'])
		except Exception as e:
			print(e)
			return { 'statusCode': 504, 'msg': 'Erro ao realizar consulta no banco de dados' }
		return { 'statusCode': 200, 'data': result}

	if method == 'create':
		if not 'entity' in params:
			return { 'statusCode': 503, 'msg': 'Parametro <entity> nao especificado' }
		entity = normalize_entity_searchable_texts(params['entity'])
		entity['id'] = table + '#' + entity['id']
		try:
			response = resource_table.put_item(Item=entity)
			result = unformat_empresa_id(table, entity)
		except Exception as e:
			print(e)
			return { 'statusCode': 504, 'msg': 'Erro ao tentar inserir o registro no banco de dados'}
		return { 'statusCode': 200, 'data': result }

	if method == 'update':
		if not 'entity' in params:
			return { 'statusCode': 503, 'msg': 'Parametro <entity> nao especificado' }
		entity = normalize_entity_searchable_texts(params['entity'])
		entity['id'] = "{}#{}".format(table, entity['id'])
		try:
			update_attributes = {}
			for key in entity:
				if key != 'id' and key != 'sort_key':
					update_attributes[key] = {
						'Value': entity[key],
						'Action': 'PUT'
					}

			resource_table.update_item(
				Key={ 'id': entity['id'] },
				AttributeUpdates=update_attributes
			)
			result = unformat_empresa_id(table, entity)
		except Exception as e:
			print(e)
			return { 'statusCode': 504, 'msg': 'Erro ao tentar alterar o registro no banco de dados'}
		return { 'statusCode': 200, 'data': result }
	if method == 'delete':
		if not 'id' in params:
			return { 'statusCode': 503, 'msg': 'Parametro <id> nao especificado' }
		id_formated = "{}#{}".format(table, params['id'])
		try:
			response = resource_table.delete_item(Key={ 'id': id_formated })
		except Exception as e:
			print(e)
			return { 'statusCode': 504, 'msg': 'Erro ao tentar remover o registro no banco de dados'}
		return { 'statusCode': 200, 'msg': 'Dado excluido com sucesso.' }

	return { 'statusCode': 200, 'data': result}

def validate_requirements(event):
    if not "method" in event:
        return { 'statusCode': 502, 'msg': 'Metodo nao especificado' }
    if not "params" in event:
        return { 'statusCode': 503, 'msg': 'Parametros nao especificado' }
    if not "table" in event["params"]:
        return { 'statusCode': 503, 'msg': 'Parametro <table> nao especificado' }
    return None

def list(table, params):
	query_filter = {}
	entity = params['table']

	# empresa_id_formated = "{}#{}".format(entity, params['empresa_id'])

	result = []
	if 'where' in params:
		for key in params['where']:
			if len(str(params['where'][key])) > 0:
				query_filter[key] = {
					'AttributeValueList': [
						params['where'][key],
					],
					'ComparisonOperator': 'CONTAINS'
				}

	if 'columns' in params:
		columns = params['columns']
		response = table.query(
			IndexName=index,
			KeyConditions={
				'sort_key': {
					'AttributeValueList': [
						params["sort_key"],
					],
					'ComparisonOperator': 'EQ'
				}
			},
			AttributesToGet=columns,
			QueryFilter=query_filter
		)
		result = response['Items']
	else:
		response = table.query(
			IndexName=index,
			KeyConditions={
				'sort_key': {
					'AttributeValueList': [
						params["sort_key"],
					],
					'ComparisonOperator': 'EQ'
				}
			},
			QueryFilter=query_filter
		)
		result = response['Items']

	for data in result:
		data = unformat_empresa_id(entity, data)

	return result

def unformat_empresa_id(entity, entity_data):
	if entity_data != None:
		entity_data['id'] = entity_data['id'].replace("{}#".format(entity), '')

	return entity_data

def normalize_entity_searchable_texts(entity_data):
	for key in entity_data:
		if 'searchable_' in key:
			entity_data[key] = unidecode.unidecode(entity_data[key.replace("searchable_", "")]).lower()
	return entity_data
