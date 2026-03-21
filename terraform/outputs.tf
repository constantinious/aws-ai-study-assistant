output "api_gateway_url" {
  description = "Base URL of the HTTP API Gateway"
  value       = "https://${aws_apigatewayv2_api.main.id}.execute-api.${var.aws_region}.amazonaws.com"
}

output "cognito_user_pool_id" {
  description = "Cognito User Pool ID"
  value       = aws_cognito_user_pool.main.id
}

output "cognito_app_client_id" {
  description = "Cognito App Client ID"
  value       = aws_cognito_user_pool_client.main.id
}

output "docs_bucket_name" {
  description = "S3 bucket for AWS documentation PDFs"
  value       = aws_s3_bucket.docs.bucket
}

output "frontend_bucket_name" {
  description = "S3 bucket for React frontend"
  value       = aws_s3_bucket.frontend.bucket
}

output "cloudfront_distribution_domain" {
  description = "CloudFront distribution domain name"
  value       = aws_cloudfront_distribution.frontend.domain_name
}

output "app_url" {
  description = "Public app URL"
  value       = "https://${local.domain_name}"
}

output "dynamodb_table_name" {
  description = "DynamoDB user progress table name"
  value       = aws_dynamodb_table.user_progress.name
}

output "lambda_function_name" {
  description = "Lambda function name"
  value       = aws_lambda_function.backend.function_name
}
