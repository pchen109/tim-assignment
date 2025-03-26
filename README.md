ansible-playbook -i "/mnt/d/OneDrive - BCIT/4.2 - A3855 - Architecture/Lab/Lab-9-redo/ansible/inventory/aws_ec2.yml"  "/mnt/d/OneDrive - BCIT/4.2 - A3855 - Architecture/Lab/Lab-9-redo/ansible/main.yml"

### Run this to avoide ignoring config file b/c of world-wide permission
export ANSIBLE_CONFIG=~/ansible.cfg

ansible-playbook -i "/mnt/d/OneDrive - BCIT/4.2 - A3855 - Architecture/Lab/Lab-9-redo (and Lab 10)/ansible/inventory/aws_ec2.yml"  "/mnt/d/OneDrive - BCIT/4.2 - A3855 - Architecture/Lab/Lab-9-redo (and Lab 10)/ansible/main.yml"


ansible-playbook -i localhost, your_playbook.yml -e "instance_ip=$(terraform output -raw instance_ip)"

### Use IP Dynamically (USE THIS ONE!!!)
ansible-playbook -i "/mnt/d/OneDrive - BCIT/4.2 - A3855 - Architecture/Lab/Lab-9-redo/ansible/inventory/aws_ec2.yml"  "/mnt/d/OneDrive - BCIT/4.2 - A3855 - Architecture/Lab/Lab-9-redo/ansible/main.yml" -e "instance_ip=$(cd '/mnt/d/OneDrive - BCIT/4.2 - A3855 - Architecture/Lab/Lab-9-redo/terraform' && terraform output -raw instance_ip)"

### Kafka Data Example 
{'type': 'user_login', 'datetime': '2025-03-23T22:23:30', 'payload': {'user_id': 'TOYDm#lGGdx', 'region': 'OCE', 'login_streak': 13, 'timestamp': '2025-12-25T21:41:43-08:00', 'trace_id': '253451a8-4e80-449b-995e-344a64f46eb5'}}

{'type': 'player_performance', 'datetime': '2025-03-23T19:19:34', 'payload': {'user_id': 'HRhOt#CPoRE', 'match_id': '21a98ab1-9607-4884-b2ba-97419f0c6dd0', 'kills': 11, 'deaths': 14, 'assists': 15, 'region': 'JP', 'game_length': 1529, 'timestamp': '2032-06-18T18:41:41-08:00', 'trace_id': '2ed7addf-e67a-4538-b382-d7b561ebde84'}}

