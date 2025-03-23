# variables for ec2 tags
variable "project_name" {
  description = "The name of the project"
  type        = string
}

variable "ec2_name" {
  description = "The value for the ec2 name tag"
  type        = string
  default     = "server"
}

variable "ec2_role" {
  description = "The value for the intended role of the ec2"
  type        = string
}

# other variables
variable "ami" {
  description = "The ID of the AMI to use for the EC2 instance"
  type        = string
}

variable "instance_type" {
  description = "The type of EC2 instance"
  type        = string
  default     = "t2.micro" # Default to t2.micro if not specified
}

variable "key_name" {
  description = "The name of the SSH key pair to use for the EC2 instance"
  type        = string
}

variable "vpc_security_group_ids" {
  description = "The IDs of the VPC security groups to associate with the EC2 instance"
  type        = list(string)
}

variable "subnet_id" {
  description = "The ID of the subnet to associate the EC2 instance with"
  type        = string
}
