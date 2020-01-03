import re
import os
import sys
from command import cmd

from setvar import *

def configure(agave_username, machine_username, machine_name, project_name):
    
    g = re.match(r'(\w+)\.(.*)',machine_name)
    os.environ["MACHINE"] = g.group(1)
    os.environ["DOMAIN"] = g.group(2)
    os.environ["MACHINE_FULL"] = machine_name
    
    
    setvar("""
    AGAVE_USERNAME="""+agave_username+"""
    MACHINE_USERNAME="""+machine_username+"""
    BASE_APP_NAME=crcollaboratory
    PORT=22
    ALLOCATION=hpc_startup_funwave
    WORK_DIR=/work/${MACHINE_USERNAME}
    HOME_DIR=/home/${MACHINE_USERNAME}
    SCRATCH_DIR=/work/${MACHINE_USERNAME}
    DEPLOYMENT_PATH=agave-deployment
    AGAVE_JSON_PARSER=jq
    PATH=$HOME/agave-model/cli/bin:$PATH
    """)
    
    
    
    readpass("MACHINE_PASSWD")
    readpass("AGAVE_PASSWD")
    readpass("PBTOK")
    
    setvar("APP_NAME=${BASE_APP_NAME}-${MACHINE}-${AGAVE_USERNAME}")
    
    #cmd("git clone https://bitbucket.org/agaveapi/cli.git")
    
    cmd("tenants-init -t agave.prod")
    
    cmd("clients-delete -u $AGAVE_USERNAME -p $AGAVE_PASSWD $APP_NAME",show=False)
    cmd("clients-create -p $AGAVE_PASSWD -S -N $APP_NAME -u $AGAVE_USERNAME",show=False)
    
    cmd("auth-tokens-create -u $AGAVE_USERNAME -p $AGAVE_PASSWD",show=False)
    
    cmd("auth-tokens-refresh")
    
    setvar("STORAGE_MACHINE=${MACHINE}-storage-${AGAVE_USERNAME}3")
    
    writefile("${STORAGE_MACHINE}.txt","""{
        "id": "${f
        }",
        "name": "${MACHINE} storage (${MACHINE_USERNAME})",
        "description": "The ${MACHINE} computer",
        "site": "${DOMAIN}",
        "type": "STORAGE",
        "storage": {
           "host": "${MACHINE_FULL}",
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
    #cmd("sshpass -f MACHINE_PASSWD.txt ssh -o StrictHostKeyChecking=no ${MACHINE_USERNAME}@${MACHINE_FULL} -p ${PORT} (sinfo || qstat -q)")
    
   
    setvar("""
    # Gather info about the machine
    # Executing this cell is essential
    MAX_TIME=72:00:00 # Max duration of a job
    # We figure out the number of processes automatically.
    # This assumes the head node and compute nodes have
    # the same number of procs.
    CPUINFO=$(sshpass -f MACHINE_PASSWD.txt ssh -o StrictHostKeyChecking=no ${MACHINE_USERNAME}@${MACHINE_FULL} -p ${PORT} lscpu)
    QUEUE=checkpt # Name of default queue
    NODES=42 # Number of nodes in queue
    """)
    g = re.search(r'(?m)CPU\(s\):\s*(\d+)',os.environ["CPUINFO"])
    os.environ["PROCS"]=g.group(1)
    print(repvar("PROCS=$PROCS"))

    setvar("EXEC_MACHINE=${MACHINE}-exec-${AGAVE_USERNAME}")
    os.environ["DIRECTIVES"]=re.sub("\n\\s*",r"\\n","""
    #PBS -A ${ALLOCATION}
    #PBS -l cput=\${AGAVE_JOB_MAX_RUNTIME}
    #PBS -l walltime=\${AGAVE_JOB_MAX_RUNTIME}
    #PBS -q \${AGAVE_JOB_BATCH_QUEUE}
    #PBS -l nodes=\${AGAVE_JOB_NODE_COUNT}:ppn=16
    """.strip())    
    writefile("${EXEC_MACHINE}.txt","""
    {
        "id": "${EXEC_MACHINE}",
        "name": "${MACHINE} (${MACHINE_USERNAME})",
        "description": "The ${MACHINE} computer",
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
                "name": "${QUEUE}",
                "default": true,
                "maxJobs": 10,
                "maxUserJobs": 10,
                "maxNodes": ${NODES},
                "maxProcessorsPerNode": ${PROCS},
                "minProcessorsPerNode": 1,
                "maxRequestedTime": "${MAX_TIME}"
            }
        ],
        "login": {
            "auth": {
             "username" : "${MACHINE_USERNAME}",
             "password" : "${MACHINE_PASSWD}",
             "type" : "PASSWORD"
            },
            "host": "${MACHINE_FULL}",
            "port": ${PORT},
            "protocol": "SSH"
        },
        "maxSystemJobs": 50,
        "maxSystemJobsPerUser": 50,
        "storage": {
            "host": "${MACHINE_FULL}",
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
        },
        "workDir": "${WORK_DIR}"
    }""")                        

    cmd("systems-addupdate -F ${EXEC_MACHINE}.txt")
    
    writefile("${APP_NAME}-wrapper.txt","""
    #!/bin/bash
    handle_trap() {
      rc=\$?
      if [ "\$rc" != 0 ]
      then
        \$(\${AGAVE_JOB_CALLBACK_FAILURE})
      fi
    }

    trap 'handle_trap' ERR EXIT
    echo 'running \${simagename} model'
    # Setting the x flag will echo every
    # command onto stderr. This is
    # for debugging, so we can see what's
    # going on.
    set -x
    set -e
    echo ==PWD=============
    # We also print out the execution
    # directory. Again, for debugging purposes.
    pwd
    echo ==JOB=============

    if [ "\${PBS_NODEFILE}" = "" ]
    then
     # When running on a system managed by Torque
     # this variable should be set. If it's not,
     # that's a problem.
     echo "The PBS_NODEFILE was not set"
     \$(\${AGAVE_JOB_CALLBACK_FAILURE})
     exit 2
    fi

    # By default, the PBS_NODEFILE lists nodes multiple
    # times, once for each MPI process that should run
    # there. We only want one MPI process per node, so
    # we create a new file with "sort -u".
    LOCAL_NODEFILE=nodefile.txt
    sort -u < \${PBS_NODEFILE} > \${LOCAL_NODEFILE}
    PROCS=\$(wc -l < \${LOCAL_NODEFILE})

    if [ "\${PROCS}" = "" ]
    then
     echo "PROCS was not set"
     \$(\${AGAVE_JOB_CALLBACK_FAILURE})
     exit 3
    fi

    # Prepare the nodes to run the image
    export SING_OPTS="--bind \$PWD:/workdir \$SING_OPTS"
    for host in \$(cat nodefile.txt)
    do
        hostfile="\$HOME/.bash.\${host}.sh"
        echo "export SING_IMAGE=/project/sbrandt/chemora/images/\${simagename}.simg" > \$hostfile
        echo "export SING_OPTS='\$SING_OPTS'" >> \$hostfile
    done

    # Create a nodefile that matches our choices at submit time
    touch nodes.txt
    for i in \$(seq 1 \${AGAVE_JOB_PROCESSORS_PER_NODE})
    do
        cat nodefile.txt >> nodes.txt
    done

    export NP=\$(wc -l < nodes.txt)

    tar xzvf input.tgz

    mkdir -p output

    /project/singularity/bin/singularity exec \$SING_OPTS /project/sbrandt/chemora/images/\${simagename}.simg bash /usr/local/bin/runapp.sh
    mv input output
    rm -f output/PRINT*
    tar cvzf output.tar.gz output
    """)
    
    cmd("files-mkdir -S ${STORAGE_MACHINE} -N ${DEPLOYMENT_PATH}")
    cmd("files-mkdir -S ${STORAGE_MACHINE} -N inputs")
    cmd("files-upload -F ${APP_NAME}-wrapper.txt -S ${STORAGE_MACHINE} ${DEPLOYMENT_PATH}/")
    
    
    writefile("test.txt","""
    parfile="input.txt"
    ${APP_NAME}-wrapper.txt
    """)
    
    cmd("files-mkdir -S ${STORAGE_MACHINE} -N ${DEPLOYMENT_PATH}")
    cmd("files-upload -F test.txt -S ${STORAGE_MACHINE} ${DEPLOYMENT_PATH}/")
    

    writefile("${APP_NAME}.txt","""
    {  
        "name":"${APP_NAME}",
        "version":"2.0",
        "label":"${APP_NAME}",
        "shortDescription":"Run ISAAC app",
        "longDescription":"",
        "deploymentSystem":"${STORAGE_MACHINE}",
        "deploymentPath":"${DEPLOYMENT_PATH}",
        "templatePath":"${APP_NAME}-wrapper.txt",
        "testPath":"test.txt",
        "executionSystem":"${EXEC_MACHINE}",
        "executionType":"HPC",
        "parallelism":"PARALLEL",
        "allocation":"${ALLOCATION}",
        "modules":[],
        "inputs":[
            {   
            "id":"input tarball",
            "details":{  
                "label":"input tarball",
                "description":"",
                "argument":null,
                "showArgument":false
            },
            "value":{  
                "default":"",
                "order":0,
                "required":false,
                "validator":"",
                "visible":true
            }
        }   

    ],
    "parameters":[
    {
      "id": "simagename",
      "value": {
        "visible": true,
        "required": false,
        "type": "string",
        "order": 0,
        "enquote": false,
        "default": "python",
        "validator": null
      },
      "details": {
        "label": "Singularity Image",
        "description": "The Singularity image to run: swan, funwave",
        "argument": null,
        "showArgument": false,
        "repeatArgument": false
      },
      "semantics": {
        "minCardinality": 0,
        "maxCardinality": 1,
        "ontology": []
      }
    }
    ],
    "outputs":[  
        {  
            "id":"Output",
            "details":{  
                "description":"The output",
                "label":"tables"
            },
            "value":{  
                "default":"",
                "validator":""
            }
        }
      ]
    }
    """)
    
    
    cmd("apps-addupdate -F ${APP_NAME}.txt")

    setvar("APP_NAME=${APP_NAME}-2.0")
    
    cmd("files-upload -F input.txt -S ${STORAGE_MACHINE}/")
    
    setvar("EMAIL=ms.ysboss@gmail.com")
    
    print ("Successfully configured Agave")

def submitJob(nodes, procs, model, jobName, execMachine, queue):
    
    setvar("MODEL="+ model)
    setvar("JOB_NAME="+ jobName)
    setvar("EXEC_MACHINE="+ execMachine)
    setvar("QUEUE="+ queue)
    
    if "PBTOK" in os.environ:
        writefile("job.txt","""
        {
            "name":"${JOB_NAME}",
            "appId": "${APP_NAME}",
            "batchQueue": "${QUEUE}",
            "maxRunTime": "72:00:00",
            "nodeCount": """+str(nodes)+""",
            "processorsPerNode": """+str(procs)+""",
            "archive": false,
            "archiveSystem": "${STORAGE_MACHINE}",
            "inputs": {
                "input tarball": "agave://${STORAGE_MACHINE}/inputs/${INPUT_DIR}/input.tgz"
            },
            "parameters": {
                "simagename":"${MODEL}"
            },
            "notifications": [
            {
                "url":"${EMAIL}",
                "event":"FINISHED",
                "persistent": true,
                "policy": {
                    "retryStrategy": "DELAYED",
                    "retryLimit": 3,
                    "retryRate": 5,
                    "retryDelay": 5,
                    "saveOnFailure": true
                    }
            },
            {
                "url":"${EMAIL}",
                "event":"FAILED",
                "persistent": true,
                "policy": {
                    "retryStrategy": "DELAYED",
                    "retryLimit": 3,
                    "retryRate": 5,
                    "retryDelay": 5,
                    "saveOnFailure": true
                    }
            },
            {
                "url":"https://www.cct.lsu.edu/~sbrandt/pushbullet.php?key=${PBTOK}&status=\${JOB_STATUS}:\${JOB_ID}",
                "event":"RUNNING",
                "persistent": true,
                "policy": {
                    "retryStrategy": "DELAYED",
                    "retryLimit": 3,
                    "retryRate": 5,
                    "retryDelay": 5,
                    "saveOnFailure": true
                    }
            },
            {
                "url":"https://www.cct.lsu.edu/~sbrandt/pushbullet.php?key=${PBTOK}&status=\${JOB_STATUS}:\${JOB_ID}",
                "event":"KILLED",
                "persistent": true,
                "policy": {
                    "retryStrategy": "DELAYED",
                    "retryLimit": 3,
                    "retryRate": 5,
                    "retryDelay": 5,
                    "saveOnFailure": true
                    }
            },
            {
                "url":"https://www.cct.lsu.edu/~sbrandt/pushbullet.php?key=${PBTOK}&status=\${JOB_STATUS}:\${JOB_ID}",
                "event":"STOPPED",
                "persistent": true,
                "policy": {
                    "retryStrategy": "DELAYED",
                    "retryLimit": 3,
                    "retryRate": 5,
                    "retryDelay": 5,
                    "saveOnFailure": true
                    }
            },
            {
                "url":"https://www.cct.lsu.edu/~sbrandt/pushbullet.php?key=${PBTOK}&status=\${JOB_STATUS}:\${JOB_ID}",
                "event":"PAUSED",
                "persistent": true,
                "policy": {
                    "retryStrategy": "DELAYED",
                    "retryLimit": 3,
                    "retryRate": 5,
                    "retryDelay": 5,
                    "saveOnFailure": true
                    }
            },
            {
                "url":"https://www.cct.lsu.edu/~sbrandt/pushbullet.php?key=${PBTOK}&status=\${JOB_STATUS}:\${JOB_ID}",
                "event":"SUBMITTING",
                "persistent": true,
                "policy": {
                    "retryStrategy": "DELAYED",
                    "retryLimit": 3,
                    "retryRate": 5,
                    "retryDelay": 5,
                    "saveOnFailure": true
                    }
            },
            {
                "url":"https://www.cct.lsu.edu/~sbrandt/pushbullet.php?key=${PBTOK}&status=\${JOB_STATUS}:\${JOB_ID}",
                "event":"QUEUED",
                "persistent": true,
                "policy": {
                    "retryStrategy": "DELAYED",
                    "retryLimit": 3,
                    "retryRate": 5,
                    "retryDelay": 5,
                    "saveOnFailure": true
                    }
            },
            {
                "url":"https://www.cct.lsu.edu/~sbrandt/pushbullet.php?key=${PBTOK}&status=\${JOB_STATUS}:\${JOB_ID}",
                "event":"FINISHED",
                "persistent": true,
                "policy": {
                    "retryStrategy": "DELAYED",
                    "retryLimit": 3,
                    "retryRate": 5,
                    "retryDelay": 5,
                    "saveOnFailure": true
                    }
            },
            {
                "url":"https://www.cct.lsu.edu/~sbrandt/pushbullet.php?key=${PBTOK}&status=\${JOB_STATUS}:\${JOB_ID}",
                "event":"FAILED",
                "persistent": true,
                "policy": {
                    "retryStrategy": "DELAYED",
                    "retryLimit": 3,
                    "retryRate": 5,
                    "retryDelay": 5,
                    "saveOnFailure": true
                    }
            }
          ]
        }
        """)
    else:
        writefile("job.txt","""
        {
            "name":"${JOB_NAME}",
            "appId": "${APP_NAME}",
            "batchQueue": "${QUEUE}",
            "maxRunTime": "72:00:00",
            "nodeCount": """+str(nodes)+""",
            "processorsPerNode": """+str(procs)+""",
            "archive": true,
            "archiveSystem": "${STORAGE_MACHINE}",
            "inputs": {
                "input tarball": "agave://${STORAGE_MACHINE}/inputs/${INPUT_DIR}/input.tgz"
            },
            "parameters": {
                "simagename":"${MODEL}"
            },
            "notifications": [
            {
                "url":"${EMAIL}",
                "event":"FINISHED",
                "persistent": true,
                "policy": {
                    "retryStrategy": "DELAYED",
                    "retryLimit": 3,
                    "retryRate": 5,
                    "retryDelay": 5,
                    "saveOnFailure": true
                    }
            },
            {
                "url":"${EMAIL}",
                "event":"FAILED",
                "persistent": true,
                "policy": {
                    "retryStrategy": "DELAYED",
                    "retryLimit": 3,
                    "retryRate": 5,
                    "retryDelay": 5,
                    "saveOnFailure": true
                    }
            }
          ]
        }
        """)

    setvar("""
    # Capture the output of the job submit command
    OUTPUT=$(jobs-submit -F job.txt)
    # Parse out the job id from the output
    JOB_ID=$(echo $OUTPUT | cut -d' ' -f4)
    """)
    
def submitBuildJob(execMachine, queue):
    
    setvar("EXEC_MACHINE="+ execMachine)
    setvar("QUEUE="+ queue)
    
    if "PBTOK" in os.environ:
        writefile("job.txt","""
        {
            "name":"build_job",
            "appId": "crcollaboratory-shelob-build-ysboss-2.0",
            "executionSystem": "${EXEC_MACHINE}",
            "batchQueue": "${QUEUE}",
            "maxRunTime": "72:00:00",
            "nodeCount": 1,
            "processorsPerNode": 8,
            "archive": false,
            "archiveSystem": "${STORAGE_MACHINE}",
            "inputs": {
                "input tarball": "agave://${STORAGE_MACHINE}/inputs/${INPUT_DIR}/env_setting.txt"
            },
            "parameters": {
            "simagename":"generic",
                "versions":"model=${MODEL_TITLE}&model_ver=${MODEL_VER}&mpich=${MPICH_VER}&hdf5=${HDF5_VER}&hypre=${HYPRE_VER}"
            },
            "notifications": [
            {
                "url":"${EMAIL}",
                "event":"FINISHED",
                "persistent":"true",
                "policy": {
                    "retryStrategy": "DELAYED",
                    "retryLimit": 3,
                    "retryRate": 5,
                    "retryDelay": 5,
                    "saveOnFailure": true
                    }
            },
            {
                "url":"${EMAIL}",
                "event":"FAILED",
                "persistent":"true",
                "policy": {
                    "retryStrategy": "DELAYED",
                    "retryLimit": 3,
                    "retryRate": 5,
                    "retryDelay": 5,
                    "saveOnFailure": true
                    }
            },
            {
                "url":"https://www.cct.lsu.edu/~sbrandt/pushbullet.php?key=${PBTOK}&status=\${JOB_STATUS}:\${JOB_ID}",
                "event":"RUNNING",
                "persistent":"true",
                "policy": {
                    "retryStrategy": "DELAYED",
                    "retryLimit": 3,
                    "retryRate": 5,
                    "retryDelay": 5,
                    "saveOnFailure": true
                    }
            },
            {
                "url":"https://www.cct.lsu.edu/~sbrandt/pushbullet.php?key=${PBTOK}&status=\${JOB_STATUS}:\${JOB_ID}",
                "event":"KILLED",
                "persistent":"true",
                "policy": {
                    "retryStrategy": "DELAYED",
                    "retryLimit": 3,
                    "retryRate": 5,
                    "retryDelay": 5,
                    "saveOnFailure": true
                    }
            },
            {
                "url":"https://www.cct.lsu.edu/~sbrandt/pushbullet.php?key=${PBTOK}&status=\${JOB_STATUS}:\${JOB_ID}",
                "event":"STOPPED",
                "persistent":"true",
                "policy": {
                    "retryStrategy": "DELAYED",
                    "retryLimit": 3,
                    "retryRate": 5,
                    "retryDelay": 5,
                    "saveOnFailure": true
                    }
            },
            {
                "url":"https://www.cct.lsu.edu/~sbrandt/pushbullet.php?key=${PBTOK}&status=\${JOB_STATUS}:\${JOB_ID}",
                "event":"PAUSED",
                "persistent":"true",
                "policy": {
                    "retryStrategy": "DELAYED",
                    "retryLimit": 3,
                    "retryRate": 5,
                    "retryDelay": 5,
                    "saveOnFailure": true
                    }
            },
            {
                "url":"https://www.cct.lsu.edu/~sbrandt/pushbullet.php?key=${PBTOK}&status=\${JOB_STATUS}:\${JOB_ID}",
                "event":"SUBMITTING",
                "persistent":"true",
                "policy": {
                    "retryStrategy": "DELAYED",
                    "retryLimit": 3,
                    "retryRate": 5,
                    "retryDelay": 5,
                    "saveOnFailure": true
                    }
            },
            {
                "url":"https://www.cct.lsu.edu/~sbrandt/pushbullet.php?key=${PBTOK}&status=\${JOB_STATUS}:\${JOB_ID}",
                "event":"QUEUED",
                "persistent":"true",
                "policy": {
                    "retryStrategy": "DELAYED",
                    "retryLimit": 3,
                    "retryRate": 5,
                    "retryDelay": 5,
                    "saveOnFailure": true
                    }
            },
            {
                "url":"https://www.cct.lsu.edu/~sbrandt/pushbullet.php?key=${PBTOK}&status=\${JOB_STATUS}:\${JOB_ID}",
                "event":"FINISHED",
                "persistent":"true",
                "policy": {
                    "retryStrategy": "DELAYED",
                    "retryLimit": 3,
                    "retryRate": 5,
                    "retryDelay": 5,
                    "saveOnFailure": true
                    }
            },
            {
                "url":"https://www.cct.lsu.edu/~sbrandt/pushbullet.php?key=${PBTOK}&status=\${JOB_STATUS}:\${JOB_ID}",
                "event":"FAILED",
                "persistent":"true",
                "policy": {
                    "retryStrategy": "DELAYED",
                    "retryLimit": 3,
                    "retryRate": 5,
                    "retryDelay": 5,
                    "saveOnFailure": true
                    }
            }
          ]
        }
        """)
    else:
        writefile("job.txt","""
        {
            "name":"build_job",
            "appId": "${APP_NAME}",
            "executionSystem": "${EXEC_MACHINE}",
            "batchQueue": "${QUEUE}",
            "maxRunTime": "72:00:00",
            "nodeCount": 1,
            "processorsPerNode": 1,
            "archive": false,
            "archiveSystem": "${STORAGE_MACHINE}",
            "inputs": {
                "input": "agave://${STORAGE_MACHINE}/inputs/${INPUT_DIR}/env_setting.sh"
            },
            "parameters": {
                "simage":"generic&model=${MODEL_TITLE}&model_ver=${MODEL_VER}&mpich=${MPICH_VER}&hdf5=${HDF5_VER}&hypre=${HYPRE_VER}"
            },
            "notifications": [
            {
                "url":"${EMAIL}",
                "event":"FINISHED",
                "persistent":"true",
                "policy": {
                    "retryStrategy": "DELAYED",
                    "retryLimit": 3,
                    "retryRate": 5,
                    "retryDelay": 5,
                    "saveOnFailure": true
                    }
            },
            {
                "url":"${EMAIL}",
                "event":"FAILED",
                "persistent":"true",
                "policy": {
                    "retryStrategy": "DELAYED",
                    "retryLimit": 3,
                    "retryRate": 5,
                    "retryDelay": 5,
                    "saveOnFailure": true
                    }
            }
          ]
        }
        """)

    setvar("""
    # Capture the output of the job submit command
    OUTPUT=$(jobs-submit -F job.txt)
    # Parse out the job id from the output
    JOB_ID=$(echo $OUTPUT | cut -d' ' -f4)
    """)
    
    
    
def configure2(agave_username, exec_machine, storage_name, project_name):
    
    setvar("""
    AGAVE_USERNAME="""+agave_username+"""
    APP_NAME="""+project_name+"""
    AGAVE_JSON_PARSER=jq
    AGAVE_CACHE_DIR=$HOME/.agave
    PATH=$HOME/agave-model/cli/bin:$PATH
    STORAGE_MACHINE="""+storage_name+"""
    DEPLOYMENT_PATH=agave-deployment
    EXEC_MACHINE="""+exec_machine+"""
    QUEUE=checkpt
    """)
   
    
    readpass("AGAVE_PASSWD")
    readpass("PBTOK")
    
    cmd("tenants-init -t agave.prod")
    
    cmd("clients-delete -u $AGAVE_USERNAME -p $AGAVE_PASSWD $APP_NAME",show=False)
    cmd("clients-create -p $AGAVE_PASSWD -S -N $APP_NAME -u $AGAVE_USERNAME",show=False)
    
    cmd("auth-tokens-create -u $AGAVE_USERNAME -p $AGAVE_PASSWD",show=False)
    
    setvar("EMAIL=ms.ysboss@gmail.com")
    print ("Successfully configured Agave")
    
#     setvar("""
#     AGAVE_USERNAME="""+agave_username+"""
#     APP_NAME="""+project_name+"""
#     AGAVE_JSON_PARSER=jq
#     PATH=$HOME/agave-model/cli/bin:$PATH
#     STORAGE_MACHINE="""+storage_name+"""
#     DEPLOYMENT_PATH=agave-deployment
#     EXEC_MACHINE="""+exec_machine+"""
#     HOME_DIR=/home/sbrandt
#     QUEUE=checkpt
#     """)
   
    
#     readpass("AGAVE_PASSWD")
#     readpass("PBTOK")
    
    
#     cmd("tenants-init -t agave.prod")
    
#     cmd("clients-delete -u $AGAVE_USERNAME -p $AGAVE_PASSWD $APP_NAME",show=False)
#     cmd("clients-create -p $AGAVE_PASSWD -S -N $APP_NAME -u $AGAVE_USERNAME",show=False)
    
#     cmd("auth-tokens-create -u $AGAVE_USERNAME -p $AGAVE_PASSWD",show=False)
    
#     setvar("EMAIL=ms.ysboss@gmail.com")
#     print ("Successfully configured Agave")


    
    
    
