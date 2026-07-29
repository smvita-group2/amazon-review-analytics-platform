resource "aws_emr_cluster" "this" {
  name          = "${var.project_name}-${var.environment}-emr"
  release_label = var.release_label

  applications = var.applications

  log_uri = var.log_uri

  service_role = var.service_role

  scale_down_behavior = "TERMINATE_AT_TASK_COMPLETION"

  keep_job_flow_alive_when_no_steps = var.keep_job_flow_alive

  termination_protection = false

  ec2_attributes {
    subnet_id        = var.subnet_id
    instance_profile = var.instance_profile

    emr_managed_master_security_group = var.master_security_group
    emr_managed_slave_security_group  = var.core_security_group
    service_access_security_group     = var.service_security_group
  }

  master_instance_group {
    instance_type  = var.master_instance_type
    instance_count = var.master_instance_count

    ebs_config {
      size                 = 100
      type                 = "gp3"
      volumes_per_instance = 1
    }
  }

  core_instance_group {
    instance_type  = var.core_instance_type
    instance_count = var.core_instance_count

    ebs_config {
      size                 = 100
      type                 = "gp3"
      volumes_per_instance = 1
    }
  }

  auto_termination_policy {
    idle_timeout = var.auto_termination_idle_timeout
  }

  configurations_json = jsonencode([
    {
      Classification = "spark"
      Properties = {
        maximizeResourceAllocation = "true"
      }
    },
    {
      Classification = "spark-defaults"
      Properties = {
        "spark.sql.adaptive.enabled"                    = "true"
        "spark.sql.adaptive.coalescePartitions.enabled" = "true"
        "spark.dynamicAllocation.enabled"               = "true"
      }
    }
  ])

  visible_to_all_users = true

  tags = {
    Name        = "${var.project_name}-${var.environment}-emr"
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}