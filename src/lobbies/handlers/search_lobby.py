import json
from src.utils.CustomEncoder import CustomEncoder
from boto3.dynamodb.conditions import Key
from src.database.dynamodb_client import query_items

def handler(event, context):
    query_params = event.get('queryStringParameters') or {}
    
    is_valid, result = validateLocationFields(query_params)
    if not is_valid:
        return result
    
    search_results = searchLobbiesByLocation(result)

    return {
        'statusCode': 200,
        'body': json.dumps(search_results, cls=CustomEncoder)
    }
    

def validateLocationFields(query_params):
    cidade = query_params.get('city')
    estado = query_params.get('state')
    esporte = query_params.get('sport_lobby')

    if not estado:
        return False,{
            'statusCode': 400, 
            'body': json.dumps({'message': 'O parâmetro "state" é obrigatório.'})
        }


    sk_prefix = f"LOC#{estado.upper()}#"

    if cidade:
        cidade_formatada = cidade.strip().lower().replace(' ', '_')
        sk_prefix += f"{cidade_formatada}#SPORT#"

        if esporte:
            esporte_formatado = esporte.strip().upper()
            sk_prefix += f"{esporte_formatado}#"
    
    return True, sk_prefix

def searchLobbiesByLocation(sk_prefix):
    return query_items(
        Key('GSI1_PK').eq('STATUS#OPEN') & Key('GSI1_SK').begins_with(sk_prefix),
        index_name='GSI1'
    )