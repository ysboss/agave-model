from time import sleep
from setvar import *
from cmd import cmd
from runagave import *

cmd("auth-tokens-refresh")

os.environ["DIRECTIVES"]=re.sub("\n\\s*",r"\\n","""
#PBS -A ${ALLOCATION}
#PBS -l cput=${AGAVE_JOB_MAX_RUNTIME}
#PBS -l walltime=${AGAVE_JOB_MAX_RUNTIME}
#PBS -q ${AGAVE_JOB_BATCH_QUEUE}
#PBS -l nodes=${AGAVE_JOB_NODE_COUNT}:ppn=16
""".strip())

writefile("${EXEC_MACHINE}-HPC.txt","""
{
    "id": "${EXEC_MACHINE}-HPC",
    "name": "${MACHINE_NAME}-HPC (${MACHINE_USERNAME})",
    "description": "The ${MACHINE_NAME} computer",
    "site": "${DOMAIN}",
    "public": false,
    "status": "UP",
    "type": "EXECUTION",
    "executionType": "HPC",
    "scheduler" : "CUSTOM_TORQUE",
    "environment": null,
    "scratchDir" : "${SCRATCH_DIR}",
    "queues": [
        {
            "customDirectives" : "${DIRECTIVES}",
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
cmd("systems-addupdate -F ${EXEC_MACHINE}-HPC.txt")
cmd("files-list -S ${EXEC_MACHINE}-HPC ./ | head -5")

writefile("queue-wrapper.txt","""
#!/bin/bash
set -x
singularity exec --bind \$PWD:/workdir --bind /var/spool --bind /etc/ssh/ssh_known_hosts /project/sbrandt/chemora/images/\${image_name}.simg mpirun -np 4 -machinefile \$PBS_NODEFILE \${exe_name} \${par_file}
# Assume the output will go to a directory named output.
# Maybe not a good assumption?
tar cvzf output.tgz output
""")
cmd("files-mkdir -S ${STORAGE_MACHINE} -N ${DEPLOYMENT_PATH}")
cmd("files-upload -F queue-wrapper.txt -S ${STORAGE_MACHINE} ${DEPLOYMENT_PATH}/")
writefile("queue-test.txt","""
queue-wrapper.txt
""")
cmd("files-mkdir -S ${STORAGE_MACHINE} -N ${DEPLOYMENT_PATH}")
cmd("files-upload -F queue-test.txt -S ${STORAGE_MACHINE} ${DEPLOYMENT_PATH}/")
writefile("queue-app.txt","""
{
   "name":"${AGAVE_USERNAME}-${MACHINE_NAME}-queue",
   "version":"1.0",
   "label":"Execute a Singularity image through the batch queue",
   "shortDescription":"Execute a Singularity image through the batch queue",
   "longDescription":"",
   "deploymentSystem":"${STORAGE_MACHINE}",
   "deploymentPath":"${DEPLOYMENT_PATH}",
   "templatePath":"queue-wrapper.txt",
   "testPath":"queue-test.txt",
   "executionSystem":"${EXEC_MACHINE}-HPC",
   "executionType":"HPC",
   "parallelism":"PARALLEL",
   "modules":[],
   "inputs":[
         {
         "id":"par_file",
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
   "parameters":[
   {
     "id" : "exe_name",
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
         "label": "The name of the executable",
         "description": "The name of the executable",
         "argument": null,
         "showArgument": false,
         "repeatArgument": false
     },
     "semantics":{
         "label": "The name of the executable",
         "description": "The name of the executable",
         "argument": null,
         "showArgument": false,
         "repeatArgument": false
     }
   },{
     "id" : "image_name",
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
         "label": "The name of the image",
         "description": "The name of the image",
         "argument": null,
         "showArgument": false,
         "repeatArgument": false
     },
     "semantics":{
         "label": "The name of the image",
         "description": "The name of the image",
         "argument": null,
         "showArgument": false,
         "repeatArgument": false
     }
   }
   ],
   "outputs":[]
}
""")
cmd("apps-addupdate -F queue-app.txt")

cmd("files-mkdir -S ${STORAGE_MACHINE} -N funwave-tvd-images")
cmd("files-upload -F input.txt -S ${STORAGE_MACHINE} funwave-tvd-images/")
runagavequeue("funwave-tvd","/usr/install/FUNWAVE-TVD/src/funwave_vessel","agave://${STORAGE_MACHINE}/funwave-tvd-images/input.txt")
