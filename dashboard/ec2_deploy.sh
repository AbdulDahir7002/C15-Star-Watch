scp -i .pemkey requirements.txt ec2-user@35.176.192.172:requirements.txt
scp -i .pemkey .env ec2-user@35.176.192.172:.env


scp -i .pemkey Home.py ec2-user@35.176.192.172:Home.py
scp -i .pemkey main.py ec2-user@35.176.192.172:main.py
scp -i .pemkey Page1.py ec2-user@35.176.192.172:Page1.py
scp -i .pemkey Page2.py ec2-user@35.176.192.172:Page2.py
scp -i .pemkey subscribe.py ec2-user@35.176.192.172:subscribe.py
scp -i .pemkey Subscriber.py ec2-user@35.176.192.172:Subscriber.py

