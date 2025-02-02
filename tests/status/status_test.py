import json
import os
import boto3
from unittest import TestCase
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError

# Definir variável de ambiente mockada
os.environ["DYNAMO_TABLE_NAME"] = "mocked_table"
os.environ["AWS_REGION"] = "us-east-1"  # Definir região para evitar erro
boto3.setup_default_session(region_name="us-east-1")  # Evita erro NoRegionError na pipeline

# Importar a Lambda após definir variáveis de ambiente
from src.status.status import lambda_handler, get_video_metadata, create_response

class TestLambdaStatus(TestCase):
    def setUp(self):
        self.event = {"pathParameters": {"video_id": "abc123"}}
        self.context = {}

    def test_lambda_handler_missing_video_id(self):
        """
        Testa erro quando o parâmetro 'video_id' está ausente.
        """
        event = {"pathParameters": {}}
        response = lambda_handler(event, self.context)
        response_body = json.loads(json.dumps(response["body"]))

        self.assertEqual(response["statusCode"], 400)
        self.assertIn("The 'video_id' parameter is required.", response_body["message"])

    @patch("src.status.status.dynamodb.Table")
    def test_lambda_handler_dynamodb_failure(self, mock_table):
        """
        Testa erro interno quando a consulta ao DynamoDB falha.
        """
        # Criar um mock da tabela e definir erro no método `query`
        mock_table_instance = MagicMock()
        mock_table.return_value = mock_table_instance
        error_response = {
            "Error": {"Code": "InternalServerError", "Message": "DynamoDB Failure"}
        }
        mock_table_instance.query.side_effect = ClientError(error_response, "Query")

        response = lambda_handler(self.event, self.context)
        response_body = json.loads(json.dumps(response["body"]))

        self.assertEqual(response["statusCode"], 500)
        self.assertIn("Internal server error.", response_body["message"])

    def test_create_response(self):
        """
        Testa se a função create_response gera uma resposta formatada corretamente.
        """
        response = create_response(200, message="Success")

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(response["body"]["message"], "Success")
