cd /agave-model
git pull
cd /usr/local/python/JetLag
git pull
cd /
randpass MND -o /usr/enable_mkuser
python /usr/local/bin/frame.py

for f in passwd shadow
do
    if [ -r /home/${f} ]
    then
        cp /home/${f} /etc/${f}
    fi
done

PORT=443
jupyterhub --ip 0.0.0.0 --port $PORT -f jup-config.py
