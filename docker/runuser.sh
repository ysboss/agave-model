#!/bin/bash
set -x
cd /home/jupuser
export HOME=/home/jupuser
#U=$(id -u)
#if [ $U = 0 ]
#then
#  echo Error: running as root >&2
#  exit 2
#fi

if [ ! -d agave-model ]
then
  git clone https://github.com/ysboss/agave-model.git

  cd agave-model

  git clone https://bitbucket.org/agaveapi/cli.git

  git config --global user.email "syuan@lsu.edu"
  git config --global user.name "Shuai Yuan"
else

  cd agave-model

  # Clean the working repo
  git checkout -- .

  # Pull the newest changes
  git pull origin $(git rev-parse --abbrev-ref HEAD)
fi

jupyter notebook --ip=0.0.0.0 --port=8003 --no-browser --allow-root
