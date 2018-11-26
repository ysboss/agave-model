if [ ! -d /home/jupuser ]
then
    echo "You need to mount the /home/jupuser directory. See instructions in the readme at https://github.com/ysboss/agave-model" >&2
    exit 2
fi
UserID=$(ls -ld /home/jupuser|awk '{print $3}')
chsh root --shell /bin/bash
if [ "$UserID" = root ]
then
    echo "You have attempted to mount /home/jupuser with either a non-existant directory or one owned by root." >&2
    bash /runuser.sh
else
    useradd -M -u $UserID jupuser -s /bin/bash
    chsh jupuser --shell /bin/bash
    sudo -u jupuser /runuser.sh
fi
