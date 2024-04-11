terraform {
  required_version = "= 0.12.26"
  backend "s3" {
    bucket         = "nmr.cyberanalyst.terraform"
    key            = "dev/admin-ui.tfstate"
    region         = "us-east-1"
    dynamodb_table = "tf-locking-table"
  }
}