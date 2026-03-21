locals {
  domain_name = "study.condevelop.net"
}

# ── ACM Certificate (must be us-east-1 for CloudFront) ───────────────────────

resource "aws_acm_certificate" "study" {
  provider          = aws.us_east_1
  domain_name       = local.domain_name
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

# ── DNS validation records in Route53 ────────────────────────────────────────

data "aws_route53_zone" "condevelop" {
  zone_id = "Z01814392FEE2T297FHXM"
}

resource "aws_route53_record" "cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.study.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      type   = dvo.resource_record_type
      record = dvo.resource_record_value
    }
  }

  zone_id = data.aws_route53_zone.condevelop.zone_id
  name    = each.value.name
  type    = each.value.type
  ttl     = 60
  records = [each.value.record]
}

resource "aws_acm_certificate_validation" "study" {
  provider                = aws.us_east_1
  certificate_arn         = aws_acm_certificate.study.arn
  validation_record_fqdns = [for r in aws_route53_record.cert_validation : r.fqdn]
}

# ── Route53 alias → CloudFront ────────────────────────────────────────────────

resource "aws_route53_record" "study" {
  zone_id = data.aws_route53_zone.condevelop.zone_id
  name    = local.domain_name
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.frontend.domain_name
    zone_id                = aws_cloudfront_distribution.frontend.hosted_zone_id
    evaluate_target_health = false
  }
}
