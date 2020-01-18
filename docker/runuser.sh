#!/bin/bash

cd /usr/local/python/JetLag
git pull

cd

if [ -r .gitconfig ]
then
    git config --global user.email "sbrandt@cct.lsu.edu"
    git config --global user.name "Steven Brandt"
fi

if [ ! -d agave-model ]
then
  git clone -b newmodel https://github.com/ysboss/agave-model.git
fi
cd ~/agave-model
echo "GIT BRANCHES"
git branch
for fn in input_*.tgz
do
   dir=${fn%.tgz}
   if [ ! -d $dir ]
   then
       echo "Unpacking $fn"
       tar xzf $fn
   fi
done

sudo tzupdate

# Get newest updates from the git repo.
git fetch

# For each file in the repo...
for i in $(git ls-files)
do
    # Check to see if file $i is locally modified...
    git diff --quiet $i
    if [ $? = 0 ]
    then
        # if it's not, then fetch the newest version.
        echo "Updating $i"
        git checkout origin/newmodel -- $i
    fi
done

SECRET_TOKEN=$(< /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c${1:-32};echo;)
echo
echo "To access the notebook, open this file in a browser copy and paste this URL:"
echo
echo " http://localhost:${PORT}/?token=${SECRET_TOKEN}"
echo
jupyter notebook --ip=0.0.0.0 --port=${PORT} --no-browser --NotebookApp.token="${SECRET_TOKEN}"

# One can also create a custom URL
# jupyter notebook --ip=0.0.0.0 --port=8003 --no-browser --NotebookApp.custom_display_url="http://localhost:8003"
