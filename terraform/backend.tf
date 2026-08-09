terraform {
  backend "s3" {
    bucket = "amazon-review-analytics-group-2"
    key    = "terraform/state/dev/terraform.tfstate"
    region = "us-east-1"
  }
}
