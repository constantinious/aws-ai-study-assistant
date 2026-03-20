# Placeholder secret — populate the value manually after apply:
# aws secretsmanager put-secret-value \
#   --secret-id aif-study/pinecone-api-key \
#   --secret-string '{"api_key":"YOUR_PINECONE_KEY"}'

resource "aws_secretsmanager_secret" "pinecone" {
  name                    = "${var.project_name}/pinecone-api-key"
  description             = "Pinecone API key for vector store access"
  recovery_window_in_days = 0
}

resource "aws_iam_role_policy" "lambda_secrets" {
  name = "${var.project_name}-lambda-secrets-policy"
  role = aws_iam_role.lambda_exec.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "ReadPineconeSecret"
        Effect   = "Allow"
        Action   = ["secretsmanager:GetSecretValue"]
        Resource = [aws_secretsmanager_secret.pinecone.arn]
      }
    ]
  })
}
