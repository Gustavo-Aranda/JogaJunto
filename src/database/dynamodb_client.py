import boto3
import os
dynamodb = boto3.resource('dynamodb')

TABLE_NAME = os.environ.get('DYNAMODB_TABLE', 'lobbies')
table = dynamodb.Table(TABLE_NAME)

def put_item(item):
    response = table.put_item(Item=item)
    return response

def get_item(key):
    response = table.get_item(Key=key)
    return response.get('Item')

def update_item(key, update_expr, expr_values, condition_expr=None, expr_names=None):
    kwargs = {
        'Key': key,
        'UpdateExpression': update_expr,
        'ExpressionAttributeValues': expr_values,
        'ReturnValues': 'UPDATED_NEW'
    }
    if condition_expr:
        kwargs['ConditionExpression'] = condition_expr
    if expr_names:
        kwargs['ExpressionAttributeNames'] = expr_names
        
    response = table.update_item(**kwargs)
    return response


def query_items(key_condition_expr, index_name=None, filter_expr=None, expr_values=None, expr_names=None):
    kwargs = {
        'KeyConditionExpression': key_condition_expr
    }
    if index_name:
        kwargs['IndexName'] = index_name
    if filter_expr:
        kwargs['FilterExpression'] = filter_expr
    if expr_values:
        kwargs['ExpressionAttributeValues'] = expr_values
    if expr_names:
        kwargs['ExpressionAttributeNames'] = expr_names

    response = table.query(**kwargs)
    return response.get('Items', [])