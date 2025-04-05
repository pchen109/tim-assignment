### Ansible
```bash
ansible-playbook -i ./inventory/aws_ec2.yml main.yml -e "instance_ip=$(cd '../terraform' && terraform output -raw instance_ip)"
```


### SSH
```bash
ssh-keygen -t ed25519 -f ~/.ssh/tim-lab
sudo chmod 600 ~/.ssh/tim-lab

eval "$(ssh-agent -s)"
ssh-add ~/.ssh/tim-lab
ssh -T git@github.com

chmod +x delete_lab_key import_lab_key
```
### WSL
```bash
wsl --update
sudo apt update
sudo apt install python3-pip
sudo apt-get install python3-boto3 python3-botocore
```
### Example processing, analyzer and consistency_check
```json
{
    "login_counts": 209,
    "max_login_streak": 77,
    "performance_counts": 213,
    "max_kills": 20,
    "last_updated": "2025-03-06T15:30:36-08:00"
}
{
    "last_updated": "2025-03-15T14:30:00Z",
    "counts": {
        "db": {
            "login_counts": 6,
            "performance_counts": 6
        },
        "queue": {
            "login_counts": 6,
            "performance_counts": 6
        },
        "processing": {
            "login_counts": 215,
            "performance_counts": 219
        }
    },
    "missing_in_db": [],
    "missing_in_queue": []
}
{
    "performance_counts": 80,
    "login_counts": 80
}
```
### mysql
```mysql
use yapper

INSERT INTO login_info (user_id, region, login_streak, timestamp, date_created, trace_id)
VALUES ('newUser123', 'NA', 10, '2025-03-27 18:30:00', '2025-03-27 18:30:00', 'new-trace-id-1234');

INSERT INTO performance_report (user_id, match_id, kills, deaths, assists, timestamp, game_length, date_created, trace_id)
VALUES ('newUser456', 'abcd1234-5678-90ef-ghij-1234567890kl', 10, 5, 7, '2025-03-27 18:30:00', 1500, '2025-03-27 18:30:00', 'new-trace-id-5678');

DELETE FROM login_info
WHERE id = 3;

DELETE FROM performance_report
WHERE id = 3;
```

### Sites
- http://localhost:8090/records
- http://localhost:8111/stats
- http://localhost:8100/stats
- http://localhost:80


### Kafka Data Example 
{'type': 'user_login', 'datetime': '2025-03-23T22:23:30', 'payload': {'user_id': 'TOYDm#lGGdx', 'region': 'OCE', 'login_streak': 13, 'timestamp': '2025-12-25T21:41:43-08:00', 'trace_id': '253451a8-4e80-449b-995e-344a64f46eb5'}}

{'type': 'player_performance', 'datetime': '2025-03-23T19:19:34', 'payload': {'user_id': 'HRhOt#CPoRE', 'match_id': '21a98ab1-9607-4884-b2ba-97419f0c6dd0', 'kills': 11, 'deaths': 14, 'assists': 15, 'region': 'JP', 'game_length': 1529, 'timestamp': '2032-06-18T18:41:41-08:00', 'trace_id': '2ed7addf-e67a-4538-b382-d7b561ebde84'}}