<p align="center">
  <img src="https://i.ibb.co/zs1zcs3/Video-Frame.png" width="30%" />
</p>

---

# Video Frame Pro - Status

Este repositório contém a implementação da **Lambda Status** do sistema **Video Frame Pro**.  
A função consulta o status de um vídeo no **DynamoDB**, retornando os detalhes do processamento.

---

## 📌 Objetivo

A função Lambda executa as seguintes tarefas:

1. **Recebe um `video_id`** como parâmetro na URL.
2. **Consulta o DynamoDB** para obter as informações do vídeo.
3. **Retorna os detalhes do vídeo**, incluindo usuário, URL, taxa de frames, status e ID da Step Function.

---

## 📂 Estrutura do Repositório

```
/src
├── status
│   ├── status.py             # Lógica principal da Lambda
│   ├── requirements.txt      # Dependências da Lambda
│   ├── __init__.py           # Inicialização do módulo
/tests
├── status
│   ├── status_test.py        # Testes unitários
│   ├── __init__.py           # Inicialização do módulo de testes
/infra
├── main.tf                   # Infraestrutura AWS (Lambda, S3, IAM, etc.)
├── outputs.tf                # Definição dos outputs Terraform
├── variables.tf              # Variáveis de configuração Terraform
├── terraform.tfvars          # Arquivo com valores das variáveis Terraform
```

---

## 🔹 Como Fazer uma Requisição

A Lambda é acionada por um endpoint **GET** no API Gateway com o seguinte formato:

```
GET https://api.example.com/video/{video_id}
```

### 📥 Exemplo de Requisição

```sh
curl -X GET "https://api.example.com/video/abc123"
```

---

## 📤 Exemplos de Resposta

### ✅ Resposta de Sucesso (200 OK)

```json
{
   "statusCode": 200,
   "body": {
      "user_name": "joao123",
      "email": "joao@email.com",
      "video_id": "abc123",
      "video_url": "https://s3.amazonaws.com/video.mp4",
      "frame_rate": 30,
      "status": "INITIATED",
      "step_function_id": "arn:aws:states:..."
   }
}
```

### ❌ Vídeo Não Encontrado (404 Not Found)

```json
{
   "statusCode": 404,
   "body": {
      "message": "Video with ID '{video_id}' not found."
   }
}
```

### ❌ Parâmetro `video_id` ausente (400 Bad Request)

```json
{
   "statusCode": 400,
   "body": {
      "message": "The 'video_id' parameter is required."
   }
}
```

---

## 🚀 Configuração e Deploy

### 1️⃣ Pré-requisitos

1. **AWS CLI** configurado (`aws configure`)
2. **Terraform** instalado (`terraform -v`)
3. Permissões para criar **Lambda Functions**, **DynamoDB** e **IAM Roles**.

### 2️⃣ Deploy da Infraestrutura

1. Navegue até o diretório `infra` e inicialize o Terraform:

```sh
cd infra
terraform init
terraform apply -auto-approve
```

### 3️⃣ Executando Testes Unitários

Execute os testes e gere o relatório de cobertura:

```sh
find tests -name 'requirements.txt' -exec pip install -r {} +
pip install coverage coverage-badge
coverage run -m unittest discover -s tests -p '*_test.py'
coverage report -m
coverage html  
```

---

## 🛠 Tecnologias Utilizadas

<p>
  <img src="https://img.shields.io/badge/AWS-232F3E?logo=amazonaws&logoColor=white" alt="AWS" />
  <img src="https://img.shields.io/badge/AWS_Lambda-4B5A2F?logo=aws-lambda&logoColor=white" alt="AWS Lambda" />
  <img src="https://img.shields.io/badge/AWS_DynamoDB-4053D6?logo=amazonaws&logoColor=white" alt="AWS DynamoDB" />
  <img src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/GitHub_Actions-2088FF?logo=github-actions&logoColor=white" alt="GitHub Actions" />
</p>

---

## 📜 Licença

Este projeto está licenciado sob a **MIT License**. Consulte o arquivo LICENSE para mais detalhes.

---

Desenvolvido com ❤️ pela equipe **Video Frame Pro**.
