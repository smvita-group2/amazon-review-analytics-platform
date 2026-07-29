resource "aws_security_group" "emr_master" {
  name        = "${var.project_name}-${var.environment}-emr-master-sg"
  description = "Security group for EMR master node"
  vpc_id      = var.vpc_id

  tags = {
    Name        = "${var.project_name}-${var.environment}-emr-master-sg"
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_security_group" "emr_core" {
  name        = "${var.project_name}-${var.environment}-emr-core-sg"
  description = "Security group for EMR core nodes"
  vpc_id      = var.vpc_id

  tags = {
    Name        = "${var.project_name}-${var.environment}-emr-core-sg"
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_security_group" "emr_service" {
  name        = "${var.project_name}-${var.environment}-emr-service-sg"
  description = "Security group for EMR service access"
  vpc_id      = var.vpc_id

  tags = {
    Name        = "${var.project_name}-${var.environment}-emr-service-sg"
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

#########################################
# MASTER <-> CORE
#########################################

resource "aws_vpc_security_group_ingress_rule" "master_from_core" {
  security_group_id            = aws_security_group.emr_master.id
  referenced_security_group_id = aws_security_group.emr_core.id

  ip_protocol = "-1"
}

resource "aws_vpc_security_group_ingress_rule" "core_from_master" {
  security_group_id            = aws_security_group.emr_core.id
  referenced_security_group_id = aws_security_group.emr_master.id

  ip_protocol = "-1"
}

#########################################
# SERVICE ACCESS
#########################################

resource "aws_vpc_security_group_ingress_rule" "master_from_service" {
  security_group_id            = aws_security_group.emr_master.id
  referenced_security_group_id = aws_security_group.emr_service.id

  ip_protocol = "-1"
}

resource "aws_vpc_security_group_ingress_rule" "core_from_service" {
  security_group_id            = aws_security_group.emr_core.id
  referenced_security_group_id = aws_security_group.emr_service.id

  ip_protocol = "-1"
}

#########################################
# EGRESS
#########################################

resource "aws_vpc_security_group_egress_rule" "master_egress" {
  security_group_id = aws_security_group.emr_master.id

  ip_protocol = "-1"
  cidr_ipv4   = "0.0.0.0/0"
}

resource "aws_vpc_security_group_egress_rule" "core_egress" {
  security_group_id = aws_security_group.emr_core.id

  ip_protocol = "-1"
  cidr_ipv4   = "0.0.0.0/0"
}

resource "aws_vpc_security_group_egress_rule" "service_egress" {
  security_group_id = aws_security_group.emr_service.id

  ip_protocol = "-1"
  cidr_ipv4   = "0.0.0.0/0"
}