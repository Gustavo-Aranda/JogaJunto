import boto3

lobbies = boto3.resource('dynamodb').Table('lobbies')