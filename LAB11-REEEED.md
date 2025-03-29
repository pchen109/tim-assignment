```bash
docker cp tim-assignment-dashboard-1:/etc/nginx/conf.d/default.conf /home/kekw/tim-lab/tim-assignment/nginx.conf

ansible-playbook -i ./inventory/aws_ec2.yml main.yml -e "instance_ip=$(cd '../terraform' && terraform output -raw instance_ip)"
```
### Remove Docker Cache & Remove Unused Images:
```bash
docker builder prune --all
docker system prune -a
```

### run compose up in venv or GG
```bash
python3 -m venv .venv
source .venv/bin/activate
```