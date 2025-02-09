import boto3
import logging
import os
import json
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

# Configuração do logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Inicialização de clientes AWS
dynamodb = boto3.resource("dynamodb")
cognito = boto3.client("cognito-idp")

# Variável de ambiente com o nome da tabela no DynamoDB
TABLE_NAME = os.environ["DYNAMO_TABLE_NAME"]
COGNITO_USER_POOL_ID = os.environ["COGNITO_USER_POOL_ID"]

def create_response(status_code, message=None, data=None):
    """
    Gera uma resposta formatada.
    """
    response = {"statusCode": status_code, "body": {}}
    if message:
        response["body"]["message"] = message
    if data:
        response["body"].update(data)
    return response

def decode_token(event):
    """
    Decodifica o token JWT usando o Cognito para obter o user_name.
    """
    try:
        logger.info("Extracting Authorization token from headers...")
        token = event["headers"].get("Authorization", "").replace("Bearer ", "")
        if not token:
            logger.warning("Authorization token is missing")
            raise ValueError("Authorization token is missing")

        logger.info("Calling Cognito to validate token...")
        cognito_client = boto3.client("cognito-idp")
        response = cognito_client.get_user(AccessToken=token)
        user_name = response["Username"]

        logger.info(f"Token validated successfully. User authenticated: {user_name}")
        return user_name
    except ClientError as e:
        logger.error(f"Failed to decode token: {e}")
        raise ValueError("Invalid token")
    except KeyError:
        logger.warning("Authorization header is missing or malformed")
        raise ValueError("Authorization header is missing")

def get_video_metadata(video_id, user_name):
    """
    Consulta o DynamoDB pelo video_id e user_name.
    """
    try:
        logger.info(f"Querying DynamoDB for video_id: {video_id}, user_name: {user_name}...")
        table = dynamodb.Table(TABLE_NAME)

        # 🔹 Ajuste: Usa KeyConditionExpression para buscar pela Partition Key (video_id) e Sort Key (user_name)
        response = table.query(
            KeyConditionExpression=Key("video_id").eq(video_id) & Key("user_name").eq(user_name)
        )

        if not response.get("Items"):
            logger.warning(f"No video found for video_id: {video_id} belonging to user: {user_name}")
            return None

        logger.info(f"Video metadata found: {response['Items'][0]}")
        return response["Items"][0]
    except ClientError as e:
        logger.error(f"Error querying DynamoDB: {e}")
        raise Exception("Error retrieving data from the database.")


def lambda_handler(event, context):
    """
    Entrada principal da Lambda.
    """
    try:
        logger.info(f"Lambda triggered with event: {json.dumps(event)}")

        # Decodificar o token para obter o user_name
        user_name = decode_token(event)

        # Verifica se há um video_id na URL (para API Gateway com path parameters)
        path_parameters = event.get("pathParameters", {})
        video_id = path_parameters.get("video_id")

        if not video_id:
            logger.warning("The 'video_id' parameter is missing in request")
            return create_response(400, message="The 'video_id' parameter is required.")

        # Busca os dados do DynamoDB
        video_metadata = get_video_metadata(video_id, user_name)

        if not video_metadata:
            logger.warning(f"Video with ID '{video_id}' not found for user '{user_name}'.")
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

    except ValueError as ve:
        logger.warning(f"Authentication error: {ve}")
        return create_response(401, message=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return create_response(500, message="Internal server error. Please try again later.")
