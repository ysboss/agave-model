import re
import os
import sys
from setvar import *
from time import sleep
from cmd import cmd
loadvar()
readpass("MACHINE_PASSWD")

writefile("${STORAGE_MACHINE}.txt","""{
    "id": "${STORAGE_MACHINE}",
    "name": "${MACHINE_NAME} storage (${MACHINE_USERNAME})",
    "description": "The ${MACHINE_NAME} computer",
    "site": "${DOMAIN}",
    "type": "STORAGE",
    "storage": {
        "host": "${MACHINE_NAME}.${DOMAIN}",
        "port": ${PORT},
        "protocol": "SFTP",
        "rootDir": "/",
        "homeDir": "${HOME_DIR}",
        "auth": {
          "username" : "${MACHINE_USERNAME}",
          "password" : "${MACHINE_PASSWD}",
          "type" : "PASSWORD"
        }
    }
}
""")
cmd("systems-addupdate -F ${STORAGE_MACHINE}.txt")
cmd("files-list -S ${STORAGE_MACHINE} ./ | head -5")
