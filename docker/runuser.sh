#!/bin/bash

if [ ! -d agave-model ]
then
  git clone https://github.com/ysboss/agave-model.git
  git config --global user.email "syuan@lsu.edu"
  git config --global user.name "Shuai Yuan"
fi
cd agave-model

sudo tzupdate

SECRET_TOKEN=$(< /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c${1:-32};echo;)
echo
echo "To access the notebook, open this file in a browser copy and paste this URL:"
echo
echo " http://localhost:8003/?token=${SECRET_TOKEN}"
echo
jupyter notebook --ip=0.0.0.0 --port=8003 --no-browser --NotebookApp.token="${SECRET_TOKEN}"

# One can also create a custom URL
# jupyter notebook --ip=0.0.0.0 --port=8003 --no-browser --NotebookApp.custom_display_url="http://localhost:8003"
