import boto3
import logging
import os
import json
from botocore.exceptions import ClientError

# Configuração do logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Inicialização de clientes AWS
dynamodb = boto3.resource("dynamodb")

# Variável de ambiente com o nome da tabela no DynamoDB
TABLE_NAME = os.environ["DYNAMO_TABLE_NAME"]

def create_response(status_code, data=None, message=None):
    """
    Gera uma resposta formatada..
    """
    response = {"statusCode": status_code, "body": {}}

    if message:
        response["body"]["message"] = message
    if data:
        response["body"].update(data)

    return response

def get_video_metadata(video_id):
    """
    Consulta o DynamoDB para obter os metadados do vídeo com base no video_id.
    """
    try:
        table = dynamodb.Table(TABLE_NAME)
        response = table.get_item(Key={"video_id": video_id})

        if "Item" not in response:
            return None

        return response["Item"]

    except ClientError as e:
        logger.error(f"Error querying DynamoDB: {e}")
        raise Exception("Error retrieving data from the database.")

def lambda_handler(event, context):
    """
    Entrada principal da Lambda.
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")

        # Verifica se há um video_id na URL (para API Gateway com path parameters)
        path_parameters = event.get("pathParameters", {})
        video_id = path_parameters.get("video_id")

        if not video_id:
            return create_response(400, message="The 'video_id' parameter is required.")

        # Busca os dados do DynamoDB
        video_metadata = get_video_metadata(video_id)

        if not video_metadata:
            return create_response(404, message=f"Video with ID '{video_id}' not found.")

        # Retorna os dados no formato esperado
        return create_response(200, data={
            "user_name": video_metadata["user_name"],
            "email": video_metadata["email"],
            "video_id": video_metadata["video_id"],
            "video_url": video_metadata["video_url"],
            "frame_rate": video_metadata["frame_rate"],
            "status": video_metadata.get("status", "UNKNOWN"),
            "step_function_id": video_metadata.get("step_function_id", "N/A")
        })

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return create_response(500, message="Internal server error. Please try again later.")
