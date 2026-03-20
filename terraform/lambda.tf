resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${var.project_name}-backend"
  retention_in_days = 14
}

resource "aws_lambda_function" "backend" {
  function_name = "${var.project_name}-backend"
  description   = "AIF Study Assistant API — FastAPI via Mangum"
  role          = aws_iam_role.lambda_exec.arn
  runtime       = "python3.12"
  architectures = ["arm64"]
  handler       = "app.main.handler"
  timeout       = 30
  memory_size   = 512

  # Placeholder zip — replaced by CI/CD on deploy
  filename         = "${path.module}/lambda_placeholder.zip"
  source_code_hash = filebase64sha256("${path.module}/lambda_placeholder.zip")

  environment {
    variables = {
      DYNAMODB_TABLE          = aws_dynamodb_table.user_progress.name
      COGNITO_USER_POOL_ID    = aws_cognito_user_pool.main.id
      COGNITO_APP_CLIENT_ID   = aws_cognito_user_pool_client.main.id
      AWS_ACCOUNT_ID          = data.aws_caller_identity.current.account_id
      BEDROCK_REGION          = var.aws_region
      PINECONE_SECRET_NAME    = "${var.project_name}/pinecone-api-key"
      ENVIRONMENT             = var.environment
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_basic,
    aws_iam_role_policy.lambda_app,
    aws_cloudwatch_log_group.lambda,
  ]
}
