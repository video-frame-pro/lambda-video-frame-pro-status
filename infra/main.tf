######### PROVEDOR AWS #################################################
# Configuração do provedor AWS
provider "aws" {
  region = var.aws_region
}

######### DADOS AWS ####################################################
# Obter informações sobre a conta AWS (ID da conta, ARN, etc.)
data "aws_caller_identity" "current" {}

# Obter o User Pool ID do Cognito no SSM
data "aws_ssm_parameter" "cognito_user_pool_id" {
  name = var.cognito_user_pool_id_ssm
}

######### FUNÇÃO LAMBDA ###############################################
# Função Lambda principal
resource "aws_lambda_function" "lambda_function" {
  function_name = "${var.prefix_name}-${var.lambda_name}-lambda"
  handler       = var.lambda_handler
  runtime       = var.lambda_runtime
  role          = aws_iam_role.lambda_role.arn
  filename      = var.lambda_zip_path
  source_code_hash = filebase64sha256(var.lambda_zip_path)

  # Variáveis de ambiente para a Lambda
  environment {
    variables = {
      DYNAMO_TABLE_NAME = var.dynamo_table_name
      COGNITO_USER_POOL_ID = data.aws_ssm_parameter.cognito_user_pool_id.value
    }
  }
}

######### GRUPO DE LOGS ###############################################
# Grupo de logs no CloudWatch para a Lambda
resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name              = "/aws/lambda/${var.prefix_name}-${var.lambda_name}-lambda"
  retention_in_days = var.log_retention_days
}

######### IAM: FUNÇÃO LAMBDA ##########################################
# Role IAM para a Lambda principal
resource "aws_iam_role" "lambda_role" {
  name = "${var.prefix_name}-${var.lambda_name}-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

# Política de permissões para a Lambda principal
resource "aws_iam_policy" "lambda_policy" {
  name = "${var.prefix_name}-${var.lambda_name}-policy"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        # Permissões para a tabela DynamoDB (inserir e buscar)
        Action   = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ],
        Effect   = "Allow",
        Resource = "arn:aws:dynamodb:${var.aws_region}:${data.aws_caller_identity.current.account_id}:table/${var.dynamo_table_name}"
      },
      {
        # Permissão para consultar o GSI (VideoIdIndex)
        Action   = [
          "dynamodb:Query",
          "dynamodb:GetItem"
        ],
        Effect   = "Allow",
        Resource = "arn:aws:dynamodb:${var.aws_region}:${data.aws_caller_identity.current.account_id}:table/${var.dynamo_table_name}/index/VideoIdIndex"
      },
      {
        # Permissões para consultar informações do Cognito
        Action   = [
          "cognito-idp:GetUser",
          "cognito-idp:AdminGetUser"
        ],
        Effect   = "Allow",
        Resource = "*"
      },
      {
        # Permissões para logs no CloudWatch
        Action   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
        Effect   = "Allow",
        Resource = "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/*"
      }
    ]
  })
}

# Anexar a política de permissões à role da Lambda
resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}
