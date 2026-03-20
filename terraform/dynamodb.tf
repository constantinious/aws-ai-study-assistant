resource "aws_dynamodb_table" "user_progress" {
  name         = "${var.project_name}-user-progress"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "user_id"
  range_key    = "domain"

  attribute {
    name = "user_id"
    type = "S"
  }

  attribute {
    name = "domain"
    type = "S"
  }

  attribute {
    name = "accuracy"
    type = "N"
  }

  global_secondary_index {
    name            = "DomainAccuracyIndex"
    hash_key        = "domain"
    range_key       = "accuracy"
    projection_type = "ALL"
  }

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled = true
  }

  ttl {
    attribute_name = "expires_at"
    enabled        = false
  }
}
