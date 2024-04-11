terraform {
  required_version = "= 1.0.8"
  backend "s3" {
    bucket         = "nmr.cyberanalyst.terraform"
    key            = "atlantis.tfstate"
    region         = "us-east-1"
    dynamodb_table = "tf-locking-table"
  }
}