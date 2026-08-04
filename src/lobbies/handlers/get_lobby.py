import json
from src.utils.CustomEncoder import CustomEncoder
from src.database.dynamodb_client import get_item

def handler(event, context):
    lobby_id = event.get('pathParameters', {}).get('lobby_id')
    
    if not lobby_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Lobby ID não fornecido'})
        }
    
    lobby = getLobby(lobby_id)
    if lobby:
        return {
            'statusCode': 200,
            'body': json.dumps(lobby, cls=CustomEncoder)
        }
    else:
        return {
            'statusCode': 404,
            'body': json.dumps({'message': 'Lobby não encontrado'})
        }

def getLobby(lobby_id):
    return get_item({'PK': f'LOBBY#{lobby_id}', 'SK': 'METADATA'})