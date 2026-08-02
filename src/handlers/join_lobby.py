import boto3
import json
from src.handlers.get_lobby import getLobby
from botocore.exceptions import ClientError

resource = boto3.resource('dynamodb')
lobbies_table = resource.Table('lobbies')

def handler (event, context):
    lobby_id = event.get('pathParameters', {}).get('lobby_id')
    body_data = json.loads(event.get('body', '{}'))
    user_id = body_data.get('user_id')

    lobby = getLobby(lobby_id)
    
    if not lobby:
        return {
            'statusCode': 404,
            'body': json.dumps({'message': 'Lobby não encontrado'})
        }
    
    if not user_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'ID do usuário não fornecido'})
        }
        
    if isLobbyFull(lobby):
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Lobby cheio'})
        }
    
    if isUserInLobby(lobby, user_id):
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Usuário já está no lobby'})
        }
        
    try:
        addPlayer(lobby, user_id)
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Não foi possível adicionar o usuário ao lobby'})
            }
        else:
            raise e
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Usuário entrou no lobby com sucesso'})
    }
    
############## Condições de aceite para entrada no lobby #######################
def isLobbyFull(lobby_data):
    
    current_players = lobby_data.get('current_players', 0)
    max_players = lobby_data.get('max_players', 0)
    
    return current_players >= max_players

def isUserInLobby(lobby, user_id):
    players = lobby.get('players', [])
    return user_id in players


def addPlayer(lobby_data, user_id):
    response = lobbies_table.update_item(
        Key={'PK': f'LOBBY#{lobby_data["lobby_id"]}', 'SK': 'METADATA'},
        UpdateExpression="SET current_players = current_players + :inc, players = list_append(if_not_exists(players, :empty_list), :new_player)",
        ConditionExpression="current_players < max_players AND (attribute_not_exists(players) OR NOT contains(players, :user_id))",       
        ExpressionAttributeValues={':inc': 1, ':new_player': [user_id], ':empty_list': [], ':user_id': user_id},
        ReturnValues="UPDATED_NEW"
    )
    
    new_current_players = response['Attributes']['current_players']
    if new_current_players == lobby_data.get('max_players'):
        lobbies_table.update_item(
            Key={'PK': f'LOBBY#{lobby_data["lobby_id"]}', 'SK': 'METADATA'},
            UpdateExpression="SET status_lobby = :full, GSI1_PK = :gsi_full",
            ExpressionAttributeValues={':full': 'FULL', ':gsi_full': 'STATUS#FULL'}
        )
    
    return response