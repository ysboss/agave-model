from time import sleep
from setvar import *
from cmd import cmd
from runagave import *

cmd("auth-tokens-refresh")

writefile("${EXEC_MACHINE}.txt","""
{
    "id": "${EXEC_MACHINE}",
    "name": "${MACHINE_NAME} (${MACHINE_USERNAME})",
    "description": "The ${MACHINE_NAME} computer",
    "site": "${DOMAIN}",
    "public": false,
    "status": "UP",
    "type": "EXECUTION",
    "executionType": "CLI",
    "scheduler" : "FORK",
    "environment": null,
    "scratchDir" : "${SCRATCH_DIR}",
    "queues": [
        {
            "name": "checkpt",
            "default": true,
            "maxJobs": 10,
            "maxUserJobs": 10,
            "maxNodes": 128,
            "maxProcessorsPerNode": 16,
            "minProcessorsPerNode": 1,
            "maxRequestedTime": "72:00:00"
        }
    ],
    "login": {
        "auth": {
          "username" : "${MACHINE_USERNAME}",
          "password" : "${MACHINE_PASSWD}",
          "type" : "PASSWORD"
        },
        "host": "${MACHINE_NAME}.${DOMAIN}",
        "port": ${PORT},
        "protocol": "SSH"
    },
    "maxSystemJobs": 50,
    "maxSystemJobsPerUser": 50,
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
    },
    "workDir": "${WORK_DIR}"
}""")
cmd("systems-addupdate -F ${EXEC_MACHINE}.txt")
cmd("files-list -S ${EXEC_MACHINE} ./ | head -5")

writefile("fork-wrapper.txt","""
#!/bin/bash
\${command}
""")
cmd("files-mkdir -S ${STORAGE_MACHINE} -N ${DEPLOYMENT_PATH}")
cmd("files-upload -F fork-wrapper.txt -S ${STORAGE_MACHINE} ${DEPLOYMENT_PATH}/")
writefile("fork-test.txt","""
command=date
fork-wrapper.txt
""")
cmd("files-mkdir -S ${STORAGE_MACHINE} -N ${DEPLOYMENT_PATH}")
cmd("files-upload -F fork-test.txt -S ${STORAGE_MACHINE} ${DEPLOYMENT_PATH}/")
writefile("fork-app.txt","""
{
   "name":"${AGAVE_USERNAME}-${MACHINE_NAME}-fork",
   "version":"1.0",
   "label":"Runs a command",
   "shortDescription":"Runs a command",
   "longDescription":"",
   "deploymentSystem":"${STORAGE_MACHINE}",
   "deploymentPath":"${DEPLOYMENT_PATH}",
   "templatePath":"fork-wrapper.txt",
   "testPath":"fork-test.txt",
   "executionSystem":"${EXEC_MACHINE}",
   "executionType":"CLI",
   "parallelism":"SERIAL",
   "modules":[],
   "inputs":[
         {
         "id":"datafile",
         "details":{
            "label":"Data file",
            "description":"",
            "argument":null,
            "showArgument":false
         },
         "value":{
            "default":"/dev/null",
            "order":0,
            "required":false,
            "validator":"",
            "visible":true
         }
      }
   ],
   "parameters":[{
     "id" : "command",
     "value" : {
       "visible":true,
       "required":true,
       "type":"string",
       "order":0,
       "enquote":false,
       "default":"/bin/date",
       "validator":null
     },
     "details":{
         "label": "Command to run",
         "description": "This is the actual command you want to run. ex. df -h -d 1",
         "argument": null,
         "showArgument": false,
         "repeatArgument": false
     },
     "semantics":{
         "label": "Command to run",
         "description": "This is the actual command you want to run. ex. df -h -d 1",
         "argument": null,
         "showArgument": false,
         "repeatArgument": false
     }
   }],
   "outputs":[]
}
""")
cmd("apps-addupdate -F fork-app.txt")

runagavecmd("lscpu")
