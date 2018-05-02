import re
import os
import sys
import subprocess

from setvar import *

def configure(agave_username, machine_username, project_name):
    
    #subprocess.call("mkdir -p ~/swan", shell = True)
    #subprocess.call("cd ~/swan", shell = True)
    
    
    setvar("""
    MACHINE=shelob
    DOMAIN=hpc.lsu.edu
    AGAVE_USERNAME="""+agave_username+"""
    MACHINE_USERNAME="""+machine_username+"""
    BASE_APP_NAME="""+project_name+"""
    PORT=22
    ALLOCATION=hpc_tutorials
    WORK_DIR=/work/${MACHINE_USERNAME}
    HOME_DIR=/home/${MACHINE_USERNAME}
    SCRATCH_DIR=/work/${MACHINE_USERNAME}
    DEPLOYMENT_PATH=agave-deployment
    MACHINE_FULL=${MACHINE}.${DOMAIN}
    AGAVE_JSON_PARSER=jq
    PATH=$HOME/swan/cli/bin:$PATH
    """)
    
    
    
    readpass("MACHINE_PASSWD")
    readpass("AGAVE_PASSWD")
    readpass("PBTOK")
    
    setvar("APP_NAME=${BASE_APP_NAME}-${MACHINE}-${AGAVE_USERNAME}")
    
    print (os.popen("git clone https://bitbucket.org/agaveapi/cli.git",'r').read())
    
    print (os.popen("tenants-init -t agave.prod",'r').read())

   
  #  cmd1 = repvar("clients-create -p $AGAVE_PASSWD -S -N $APP_NAME -u $AGAVE_USERNAME")
    
  #  output = os.popen(cmd1,'r')
  #  print (output.read())
    print (os.popen(repvar("clients-create -p $AGAVE_PASSWD -S -N $APP_NAME -u $AGAVE_USERNAME"),'r').read())
    
    print (os.popen(repvar("auth-tokens-create -u $AGAVE_USERNAME -p $AGAVE_PASSWD"),'r').read())
    
    print (os.popen(repvar("jsonpki --public ${MACHINE}-key.pub > ${MACHINE}-key.pub.txt"),'r').read())
    
    print (os.popen(repvar("jsonpki --private ${MACHINE}-key > ${MACHINE}-key.txt"),'r').read())
    
    print (os.popen("auth-tokens-refresh",'r').read())
    
    os.environ["PUB_KEY"]=readfile("${MACHINE}-key.pub.txt").strip()
    os.environ["PRIV_KEY"]=readfile("${MACHINE}-key.txt").strip()
    setvar("STORAGE_MACHINE=${MACHINE}-storage-${AGAVE_USERNAME}3")
    
    writefile("${STORAGE_MACHINE}.txt","""{
        "id": "${STORAGE_MACHINE}",
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
             "password" : "${MACHINE_PASSWORD}",
             "type" : "PASSWORD"
           }
     }
    }
    """)
    
    print (os.popen(repvar("systems-addupdate -F ${STORAGE_MACHINE}.txt"),'r').read())
    print (os.popen(repvar("ssh -o IdentityFile=${MACHINE}-key ${MACHINE_USERNAME}@${MACHINE_FULL} -p ${PORT} (sinfo || qstat -q)"),'r').read())
    
   
    setvar("""
    # Gather info about the machine
    # Executing this cell is essential
    MAX_TIME=72:00:00 # Max duration of a job
    # We figure out the number of processes automatically.
    # This assumes the head node and compute nodes have
    # the same number of procs.
    CPUINFO=$(ssh -o "IdentityFile=${MACHINE}-key" ${MACHINE_USERNAME}@${MACHINE_FULL} -p ${PORT} lscpu)
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
             "password" : "${MACHINE_PASSWORD}",
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
             "password" : "${MACHINE_PASSWORD}",
             "type" : "PASSWORD"
            }
         }
        },
        "workDir": "${WORK_DIR}"
    }""")                        

    print (os.popen(repvar("systems-addupdate -F ${EXEC_MACHINE}.txt"),'r').read())
    
    writefile("swan-wrapper.txt","""
    #!/bin/bash
    echo 'running swan model'
    # Setting the x flag will echo every
    # command onto stderr. This is
    # for debugging, so we can see what's
    # going on.
    set -x
    echo ==ENV=============
    # The env command prints out the
    # entire execution environment. This
    # is also present for debugging purposes.
    env
    echo ==PWD=============
    # We also print out the execution
    # directory. Again, for debugging purposes.
    pwd
    echo ==JOB=============
    EXE_DIR=/home/${MACHINE_USERNAME}/ISAAC

    if [ "\${PBS_NODEFILE}" = "" ]
    then
     # When running on a system managed by Torque
     # this variable should be set. If it's not,
     # that's a problem.
     echo "The PBS_NODEFILE was not set"
     
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
     
     exit 3
    fi

    # Execute our MPI command.
    cd input
    mpiexec --machinefile \${PBS_NODEFILE} swan.exe
    rm -f PRINT-*
    cd ..
    cp -r input output
    tar -zcvf output.tar.gz output
    """)
    
    print (os.popen(repvar("files-mkdir -S ${STORAGE_MACHINE} -N ${DEPLOYMENT_PATH}"),'r').read())
    print (os.popen(repvar("files-upload -F swan-wrapper.txt -S ${STORAGE_MACHINE} ${DEPLOYMENT_PATH}/"),'r').read())
    
    
    writefile("test.txt","""
    parfile="input.txt"
    swan-wrapper.txt
    """)
    
    print (os.popen(repvar("files-mkdir -S ${STORAGE_MACHINE} -N ${DEPLOYMENT_PATH}"),'r').read())
    print (os.popen(repvar("files-upload -F test.txt -S ${STORAGE_MACHINE} ${DEPLOYMENT_PATH}/"),'r').read())
    

    writefile("${APP_NAME}.txt","""
    {  
        "name":"${APP_NAME}",
        "version":"2.0",
        "label":"SWAN",
        "shortDescription":"Run ISAAC app",
        "longDescription":"",
        "deploymentSystem":"${STORAGE_MACHINE}",
        "deploymentPath":"${DEPLOYMENT_PATH}",
        "templatePath":"swan-wrapper.txt",
        "testPath":"test.txt",
        "executionSystem":"${EXEC_MACHINE}",
        "executionType":"HPC",
        "parallelism":"PARALLEL",
        "allocation":"${ALLOCATION}",
        "modules":[],
        "inputs":[
            {   
            "id":"parfile",
            "details":{  
                "label":"null parfile",
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
    "parameters":[],
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
    
    
    print (os.popen(repvar("apps-addupdate -F ${APP_NAME}.txt"),'r').read())
    
    writefile("input.txt","")
    
    print (os.popen(repvar("files-upload -F input.txt -S ${STORAGE_MACHINE}/ISAAC"),'r').read())
    
    
    setvar("EMAIL=ms.ysboss@gmail.com")

def submitJob(nodes,procs):
    
    setvar("JOB_NAME=test-job-3")
    
    writefile("job.txt","""
    {
        "name":"${JOB_NAME}",
        "appId": "${APP_NAME}-2.0",
        "executionSystem": "${EXEC_MACHINE}",
        "batchQueue": "${QUEUE}",
        "maxRunTime": "01:00:00",
        "nodeCount": """+str(nodes)+""",
        "processorsPerNode": """+str(procs)+""",
        "archive": false,
        "archiveSystem": "${STORAGE_MACHINE}",
        "inputs": {
            "parfile": ""
        },
        "parameters": {
        },
        "notifications": [
        {
            "url":"${EMAIL}",
            "event":"FINISHED",
            "persistent":false
        },
        {
            "url":"${EMAIL}",
            "event":"FAILED",
            "persistent":false
        },
        {
            "url":"https://www.cct.lsu.edu/~sbrandt/pushbullet.php?key=${PBTOK}&status=\${JOB_STATUS}:\${JOB_ID}",
            "event":"FINISHED",
            "persistent":"false"
        },
        {
            "url":"https://www.cct.lsu.edu/~sbrandt/pushbullet.php?key=${PBTOK}&status=\${JOB_STATUS}:\${JOB_ID}",
            "event":"FAILED",
            "persistent":"false"
        }
      ]
    }
    """)

    #os.system('jobs-submit -F job.txt')
    #subprocess.call("jobs-submit -F job.txt", stdout=subprocess.PIPE, shell = True)
    setvar("""
    # Capture the output of the job submit command
    OUTPUT=$(jobs-submit -F job.txt)
    # Parse out the job id from the output
    JOB_ID=$(echo $OUTPUT | cut -d' ' -f4)
    """)
    
    
    
    
    
    
    
    
    
    
    
