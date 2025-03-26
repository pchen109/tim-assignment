ansible-playbook -i "/mnt/d/OneDrive - BCIT/4.2 - A3855 - Architecture/Lab/Lab-9-redo/ansible/inventory/aws_ec2.yml"  "/mnt/d/OneDrive - BCIT/4.2 - A3855 - Architecture/Lab/Lab-9-redo/ansible/main.yml"

### Run this to avoide ignoring config file b/c of world-wide permission
export ANSIBLE_CONFIG=~/ansible.cfg

ansible-playbook -i "/mnt/d/OneDrive - BCIT/4.2 - A3855 - Architecture/Lab/Lab-9-redo (and Lab 10)/ansible/inventory/aws_ec2.yml"  "/mnt/d/OneDrive - BCIT/4.2 - A3855 - Architecture/Lab/Lab-9-redo (and Lab 10)/ansible/main.yml"


ansible-playbook -i localhost, your_playbook.yml -e "instance_ip=$(terraform output -raw instance_ip)"

### Use IP Dynamically
ansible-playbook -i "/mnt/d/OneDrive - BCIT/4.2 - A3855 - Architecture/Lab/Lab-9-redo/ansible/inventory/aws_ec2.yml"  "/mnt/d/OneDrive - BCIT/4.2 - A3855 - Architecture/Lab/Lab-9-redo/ansible/main.yml" -e "instance_ip=$(cd '/mnt/d/OneDrive - BCIT/4.2 - A3855 - Architecture/Lab/Lab-9-redo/terraform' && terraform output -raw instance_ip)"

