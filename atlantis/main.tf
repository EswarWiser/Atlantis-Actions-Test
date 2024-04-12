provider "aws" {
  region = "us-east-1"

  allowed_account_ids = [
    "462671926206",
  ]
}

data "terraform_remote_state" "vpc" {
  backend = "s3"
  config = {
    bucket = "nmr.cyberanalyst.terraform"
    key    = "vpc.tfstate"
    region = "us-east-1"
  }
}

module "atlantis" {
  source = "git::git@github.com:Gazaro/terraform-modules.git//modules/atlantis"

  github_organization     = "EswarWiser"
  github_repository_names = ["Atlantis-Actions-test"]
  github_repository_owners = [
    "jaimemarco",       # Jaime Marco
    "alejandro-celada", # Alejandro Celada
    "EswarWiser"
  ]

  force_recreate_token = "v2"
  atlantis_github_user_token = ""

  default_terraform_version = "0.12.26"

  vpc_id              = data.terraform_remote_state.vpc.outputs.vpc_id
  private_subnet_ids  = data.terraform_remote_state.vpc.outputs.private_subnet_ids
  public_subnet_ids   = data.terraform_remote_state.vpc.outputs.public_subnet_ids
  route53_zone_name   = "mapintel.wiser.com"
  acm_certificate_arn = ""
}