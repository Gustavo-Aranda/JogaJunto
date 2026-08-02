import boto3
import json
import uuid
from decimal import Decimal

resource = boto3.resource('dynamodb')
lobbies_table = resource.Table('lobbies')

def handler(event, context):
    try:
        lobby_data = json.loads(event.get('body', '{}'))
        if not lobby_data:
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
            'lobby_id': lobby_item['lobby_id']
            })
    }

def validateLobbyData(lobby_data):
    required_fields = ['lobby_name', 'max_players', 'match_time', 'location', 'price', 'sport']
    
    for field in required_fields:
        if field not in lobby_data:
            return False, {
                'statusCode': 400,
                'body': json.dumps({
                    'message': f'Campo obrigatório ausente: {field}'
                    })
            }
            
        if field in ['lobby_name', 'match_time', 'sport']:
            if not isinstance(lobby_data[field], str) or not lobby_data[field].strip():
                return False, {
                    'statusCode': 400,
                    'body': json.dumps({
                        'message': f'Campo {field} deve ser uma string não vazia'
                    })
                }
            
        if field in ['max_players', 'price']:
            if not isinstance(lobby_data[field], int) or lobby_data[field] < 0:
                return False, {
                    'statusCode': 400,
                    'body': json.dumps({
                        'message': f'Campo {field} deve ser um inteiro não negativo'
                    })
                }
        
        if field == 'location':
            if not isinstance(lobby_data['location'], dict):
                return False, {
                    'statusCode': 400,
                    'body': json.dumps({
                        'message': f'Campo {field} deve ser um objeto JSON'
                    })
                }
            loc = lobby_data['location']
            loc_required_fields = ['name', 'address', 'city', 'state', 'lat', 'lng']
            for loc_field in loc_required_fields:
                if loc_field not in loc:
                    return False, {
                        'statusCode': 400,
                        'body': json.dumps({
                            'message': f'Campo obrigatório ausente em location: {loc_field}'
                        })
                    }
  
    return True, None

def putLobby(lobby_data):
    lobby_id = str(uuid.uuid4())
    loc      = lobby_data['location']
    
    cidade = str(loc['city']).strip().lower().replace(' ', '_')
    estado = str(loc['state']).upper().strip()
    esporte = str(lobby_data['sport']).upper()
    gsi1_sk = f"LOC#{estado}#{cidade}SPORT#{esporte}#TIME#{lobby_data['match_time']}"
    
    lobby_item = {
        'PK': f'LOBBY#{lobby_id}',
        'SK': 'METADATA',
        'GSI1_PK': 'STATUS#OPEN',
        'GSI1_SK': gsi1_sk,
        'lobby_id': lobby_id,
        'lobby_name': lobby_data['lobby_name'],
        'sport': esporte,
        'max_players': lobby_data['max_players'],
        'current_players': 0,
        'status': 'OPEN',
        'match_time': lobby_data['match_time'],
        'price': lobby_data['price'],
        'location': {
            'name': loc['name'],
            'address': loc['address'],
            'city': loc['city'],
            'state': loc['state'],
            'lat': Decimal(str(loc['lat'])),
            'lng': Decimal(str(loc['lng']))
        }
    }
    
    lobbies_table.put_item(Item=lobby_item)
    
    return lobby_item