import boto3
import json
import uuid

resource = boto3.resource('dynamodb')
lobbies_table = resource.Table('lobbies')

def handler(event, context):
    try:
        lobby_data = json.loads(event.get('body', '{}'))
        if lobby_data is None:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Dados do lobby não fornecidos'})
            }
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Dados do lobby inválidos'})
        }
    
    
    validation_result, validation_response = validateLobbyData(lobby_data)
    if not validation_result:
        return validation_response
    
    
    lobby_item = putLobby(lobby_data)
    
    return {
        'statusCode': 201,
        'body': json.dumps({
            'message': f'Lobby {lobby_item["lobby_id"]} criada com sucesso.', 
            'lobby': lobby_item
            })
    }

def validateLobbyData(lobby_data):
    required_fields = ['lobby_name', 'max_players', 'match_time', 'location', 'price']
    
    for field in required_fields:
        if field not in lobby_data:
            return False, {
                'statusCode': 400,
                'body': json.dumps({
                    'message': f'Campo obrigatório ausente: {field}'
                    })
            }
            
        if field == 'lobby_name' or field == 'location' or field == 'match_time':
            if not isinstance(lobby_data[field], str) or not lobby_data[field].strip():
                return False, {
                    'statusCode': 400,
                    'body': json.dumps({
                        'message': f'Campo {field} deve ser uma string não vazia'
                    })
                }
            
        if field == 'max_players' or field == 'price':
            if not isinstance(lobby_data[field], int) or lobby_data[field] < 0:
                return False, {
                    'statusCode': 400,
                    'body': json.dumps({
                        'message': f'Campo {field} deve ser um inteiro não negativo'
                    })
                }
  
    return True, None

def putLobby(lobby_data):
    lobby_id = str(uuid.uuid4())
    lobby_item = {
        'PK': f'LOBBY#{lobby_id}',
        'SK': 'METADATA',
        'lobby_id': lobby_id,
        'lobby_name': lobby_data['lobby_name'],
        'max_players': lobby_data['max_players'],
        'current_players': 0,
        'status': 'OPEN',
        'match_time': lobby_data['match_time'],
        'location': lobby_data['location'],
        'price': lobby_data['price']
    }
    
    lobbies_table.put_item(Item=lobby_item)
    
    return lobby_item