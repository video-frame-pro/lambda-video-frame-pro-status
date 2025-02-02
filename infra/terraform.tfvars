######### PREFIXO DO PROJETO ###########################################
prefix_name = "video-frame-pro" # Prefixo para nomear todos os recursos

######### AWS INFOS ####################################################
aws_region = "us-east-1" # Região AWS onde os recursos serão provisionados

######### PROJECT INFOS ################################################
lambda_name     = "status" # Nome da função Lambda principal
lambda_handler  = "status.lambda_handler" # Handler da função Lambda principal
lambda_zip_path = "../lambda/status/status.zip" # Caminho para o ZIP da função Lambda
lambda_runtime  = "python3.12" # Runtime da função Lambda principal

######### DYNAMO INFOS #################################################
dynamo_table_name = "video-frame-pro-metadata-table" # Nome da tabela DynamoDB para armazenar informações

######### LOGS CLOUD WATCH #############################################
log_retention_days = 7 # Dias para retenção dos logs no CloudWatch
