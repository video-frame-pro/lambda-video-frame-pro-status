import json
import os
import boto3
from unittest import TestCase
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError

# Definir variável de ambiente mockada
os.environ["DYNAMO_TABLE_NAME"] = "mocked_table"

# Garantir que boto3 use a região definida
boto3.setup_default_session(region_name=os.environ["AWS_REGION"])

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

    @patch("boto3.resource")
    def test_lambda_handler_dynamodb_failure(self, mock_boto3_resource):
        """
        Testa erro interno quando a consulta ao DynamoDB falha.
        """
        mock_table = MagicMock()
        mock_boto3_resource.return_value.Table.return_value = mock_table
        error_response = {"Error": {"Code": "InternalServerError", "Message": "DynamoDB Failure"}}
        mock_table.get_item.side_effect = ClientError(error_response, "GetItem")

        response = lambda_handler(self.event, self.context)
        response_body = response["body"]

        self.assertEqual(response["statusCode"], 500)
        self.assertIn("Internal server error.", response_body["message"])

    def test_create_response(self):
        """
        Testa se a função create_response gera uma resposta formatada corretamente.
        """
        response = create_response(200, message="Success")

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(response["body"]["message"], "Success")
