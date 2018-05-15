if [ ! -d /home/jupuser ]
then
    echo "You need to mount the /home/jupuser directory. See instructions in the readme at https://github.com/ysboss/agave-model" >&2
    exit 2
fi
UserID=$(ls -ld /home/jupuser|awk '{print $3}')
if [ "$UserID" = root ]
then
    echo "You have attempted to mount /home/jupuser with either a non-existant directory or one owned by root." >&2
    exit 3
fi
useradd -M -u $UserID jupuser
sudo -u jupuser /runuser.sh
