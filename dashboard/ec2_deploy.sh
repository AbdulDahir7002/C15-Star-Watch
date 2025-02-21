scp -i .pemkey requirements.txt ec2-user@35.176.192.172:dashboard/requirements.txt
scp -i .pemkey .env ec2-user@35.176.192.172:dashboard/.env


scp -i .pemkey Home.py ec2-user@35.176.192.172:dashboard/Home.py
scp -i .pemkey main.py ec2-user@35.176.192.172:dashboard/main.py
scp -i .pemkey Page1.py ec2-user@35.176.192.172:dashboard/Page1.py
scp -i .pemkey Page2.py ec2-user@35.176.192.172:dashboard/Page2.py
scp -i .pemkey subscribe.py ec2-user@35.176.192.172:dashboard/subscribe.py
scp -i .pemkey Subscriber.py ec2-user@35.176.192.172:dashboard/Subscriber.py
scp -i .pemkey Unsubscribe.py ec2-user@35.176.192.172:dashboard/Unsubscribe.py

