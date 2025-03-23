output "instance_ip_addr" {
  description = "The public IP of the EC2 instance."
  value       = aws_instance.web.public_ip
}

output "instance_dns_name" {
  description = "The public DNS of the EC2 instance."
  value       = aws_instance.web.public_dns
}

output "instance_id" {
  description = "The ID of the EC2 instance."
  value       = aws_instance.web.id
}
