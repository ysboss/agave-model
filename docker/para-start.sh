#!/bin/bash

sudo tzupdate

export PASSWORD=$(< /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c${1:-32};echo;)
echo
echo "To access the notebook, open this file in a browser copy and paste this URL:"
echo
echo "User is: cloudbroker"
echo "Password is: $PASSWORD"
echo
/opt/launcher/starter.sh
