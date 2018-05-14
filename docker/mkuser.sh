UserID=$(ls -ld /home/jupuser|awk '{print $3}')
useradd -M -u $UserID jupuser
sudo -u jupuser /runuser.sh
