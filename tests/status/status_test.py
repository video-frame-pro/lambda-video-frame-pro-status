import json
import os
import boto3
from unittest import TestCase
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError

# Definir variável de ambiente mockada
os.environ["DYNAMO_TABLE_NAME"] = "mocked_table"
os.environ["COGNITO_USER_POOL_ID"] = "mocked_pool"
os.environ["AWS_REGION"] = "us-east-1"  # Definir região para evitar erro
boto3.setup_default_session(region_name="us-east-1")  # Evita erro NoRegionError na pipeline

# Importar a Lambda após definir variáveis de ambiente
from src.status.status import lambda_handler, get_video_metadata, create_response, decode_token

class TestLambdaStatus(TestCase):
    def setUp(self):
        self.event = {
            "headers": {"Authorization": "Bearer mock_token"},
            "pathParameters": {"video_id": "abc123"}
        }
        self.context = {}

    @patch("src.status.status.decode_token")
    def test_lambda_handler_missing_video_id(self, mock_decode_token):
        """
        Testa erro quando o parâmetro 'video_id' está ausente.
        """
        mock_decode_token.return_value = "mock_user"
        event = {"headers": {"Authorization": "Bearer mock_token"}, "pathParameters": {}}

        response = lambda_handler(event, self.context)
        response_body = response["body"]

        self.assertEqual(response["statusCode"], 400)
        self.assertIn("The 'video_id' parameter is required.", response_body["message"])

    @patch("src.status.status.dynamodb.Table")
    @patch("src.status.status.decode_token")
    def test_lambda_handler_dynamodb_failure(self, mock_decode_token, mock_table):
        """
        Testa erro interno quando a consulta ao DynamoDB falha.
        """
        mock_decode_token.return_value = "mock_user"

        # Criar um mock da tabela e definir erro no método `query`
        mock_table_instance = MagicMock()
        mock_table.return_value = mock_table_instance
        error_response = {
            "Error": {"Code": "InternalServerError", "Message": "DynamoDB Failure"}
        }
        mock_table_instance.query.side_effect = ClientError(error_response, "Query")

        response = lambda_handler(self.event, self.context)
        response_body = response["body"]

        self.assertEqual(response["statusCode"], 500)
        self.assertIn("Internal server error.", response_body["message"])

    def test_create_response(self):
        """
        Testa se a função create_response gera uma resposta formatada corretamente.
        """
        response = create_response(200, message="Success")
        response_body = response["body"]

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(response_body["message"], "Success")

    @patch("src.status.status.boto3.client")
    def test_decode_token_success(self, mock_boto3_client):
        """
        Testa a decodificação bem-sucedida do token Cognito.
        """
        mock_cognito = MagicMock()
        mock_boto3_client.return_value = mock_cognito
        mock_cognito.get_user.return_value = {"Username": "mock_user"}

        event = {"headers": {"Authorization": "Bearer mock_token"}}
        user_name = decode_token(event)

        self.assertEqual(user_name, "mock_user")

    @patch("src.status.status.boto3.client")
    def test_decode_token_invalid_token(self, mock_boto3_client):
        """
        Testa erro quando o token Cognito é inválido.
        """
        mock_cognito = MagicMock()
        mock_boto3_client.return_value = mock_cognito
        mock_cognito.get_user.side_effect = ClientError(
            {"Error": {"Code": "NotAuthorizedException", "Message": "Invalid token"}}, "GetUser"
        )

        event = {"headers": {"Authorization": "Bearer invalid_token"}}

        with self.assertRaises(ValueError) as context:
            decode_token(event)

        self.assertEqual(str(context.exception), "Invalid token")

    @patch("src.status.status.boto3.client")
    def test_decode_token_missing_token(self, mock_boto3_client):
        """
        Testa erro quando o token não está presente no cabeçalho.
        """
        event = {"headers": {}}

        with self.assertRaises(ValueError) as context:
            decode_token(event)

        self.assertEqual(str(context.exception), "Authorization token is missing")

    @patch("src.status.status.dynamodb.Table")
    @patch("src.status.status.decode_token")
    def test_get_video_metadata_success(self, mock_decode_token, mock_table):
        """
        Testa a recuperação bem-sucedida dos metadados do vídeo no DynamoDB.
        """
        mock_decode_token.return_value = "mock_user"

        mock_table_instance = MagicMock()
        mock_table.return_value = mock_table_instance
        mock_table_instance.query.return_value = {"Items": [{"video_id": "abc123", "user_name": "mock_user"}]}

        video_metadata = get_video_metadata("abc123", "mock_user")

        self.assertIsNotNone(video_metadata)
        self.assertEqual(video_metadata["video_id"], "abc123")

    @patch("src.status.status.dynamodb.Table")
    @patch("src.status.status.decode_token")
    def test_get_video_metadata_not_found(self, mock_decode_token, mock_table):
        """
        Testa caso em que o vídeo não é encontrado no DynamoDB.
        """
        mock_decode_token.return_value = "mock_user"

        mock_table_instance = MagicMock()
        mock_table.return_value = mock_table_instance
        mock_table_instance.query.return_value = {"Items": []}  # Nenhum item encontrado

        video_metadata = get_video_metadata("abc123", "mock_user")

        self.assertIsNone(video_metadata)
