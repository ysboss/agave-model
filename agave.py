import re
import os
import sys
import subprocess

from setvar import *

def cmd(cmd,show=True):
    cmd = repvar(cmd)
    if show:
        print('cmd:',cmd)
        os.write(1,(cmd+'\n').encode())
    os.system(cmd + " 2>&1")

def configure(agave_username, machine_username, machine_name, project_name):
    
    #subprocess.call("mkdir -p ~/swan", shell = True)
    #subprocess.call("cd ~/swan", shell = True)
    g = re.match(r'(\w+)\.(.*)',machine_name)
    os.environ["MACHINE"] = g.group(1)
    os.environ["DOMAIN"] = g.group(2)
    os.environ["MACHINE_FULL"] = machine_name
    
    
    setvar("""
    AGAVE_USERNAME="""+agave_username+"""
    MACHINE_USERNAME="""+machine_username+"""
    BASE_APP_NAME="""+project_name+"""
    PORT=22
    ALLOCATION=hpc_tutorials
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
    
    writefile("swan-wrapper.txt","""
    #!/bin/bash
    echo 'running swan model'
    # Setting the x flag will echo every
    # command onto stderr. This is
    # for debugging, so we can see what's
    # going on.
    set -x
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

    # Prepare the nodes to run the swan image
    export SING_OPTS="--bind \$PWD:/workdir --bind /var/spool --bind /etc/ssh/ssh_known_hosts --bind /work --bind /var/spool"
    for host in \$(cat nodefile.txt)
    do
        hostfile="\$HOME/.bash.\${host}.sh"
        echo "export SING_IMAGE=/project/sbrandt/chemora/images/swan.simg" > \$hostfile
        echo "export SING_OPTS='\$SING_OPTS'" >> \$hostfile
    done

    # Create a nodefile that matches our choices at submit time
    touch nodes.txt
    for i in \$(seq 1 \${AGAVE_JOB_PROCESSORS_PER_NODE})
    do
        cat nodefile.txt >> nodes.txt
    done

    NP=\$(wc -l < nodes.txt)

    tar xzvf input.tgz

    # Create a file to run the code
    echo echo RUNNING SWAN > input/runswan.sh
    echo cd /workdir/input >> input/runswan.sh
    echo mpirun -np \$NP -machinefile /workdir/nodes.txt /model/swan4120/swan.exe >> input/runswan.sh

    /project/singularity/2.4.2/bin/singularity exec \$SING_OPTS /project/sbrandt/chemora/images/swan.simg bash /workdir/input/runswan.sh
    mv input output
    tar cvzf output.tar.gz output
    """)
    
    cmd("files-mkdir -S ${STORAGE_MACHINE} -N ${DEPLOYMENT_PATH}")
    cmd("files-upload -F swan-wrapper.txt -S ${STORAGE_MACHINE} ${DEPLOYMENT_PATH}/")
    
    
    writefile("test.txt","""
    parfile="input.txt"
    swan-wrapper.txt
    """)
    
    cmd("files-mkdir -S ${STORAGE_MACHINE} -N ${DEPLOYMENT_PATH}")
    cmd("files-upload -F test.txt -S ${STORAGE_MACHINE} ${DEPLOYMENT_PATH}/")
    

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
    
    
    cmd("apps-addupdate -F ${APP_NAME}.txt")
    
    writefile("input.txt","")
    
    cmd("files-upload -F input.txt -S ${STORAGE_MACHINE}/")
    
    
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
            "parfile": "input.tgz"
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
            "event":"RUNNING",
            "persistent":"false"
        },
        {
            "url":"https://www.cct.lsu.edu/~sbrandt/pushbullet.php?key=${PBTOK}&status=\${JOB_STATUS}:\${JOB_ID}",
            "event":"KILLED",
            "persistent":"false"
        },
        {
            "url":"https://www.cct.lsu.edu/~sbrandt/pushbullet.php?key=${PBTOK}&status=\${JOB_STATUS}:\${JOB_ID}",
            "event":"STOPPED",
            "persistent":"false"
        },
        {
            "url":"https://www.cct.lsu.edu/~sbrandt/pushbullet.php?key=${PBTOK}&status=\${JOB_STATUS}:\${JOB_ID}",
            "event":"PAUSED",
            "persistent":"false"
        },
        {
            "url":"https://www.cct.lsu.edu/~sbrandt/pushbullet.php?key=${PBTOK}&status=\${JOB_STATUS}:\${JOB_ID}",
            "event":"SUBMITTING",
            "persistent":"false"
        },
        {
            "url":"https://www.cct.lsu.edu/~sbrandt/pushbullet.php?key=${PBTOK}&status=\${JOB_STATUS}:\${JOB_ID}",
            "event":"QUEUED",
            "persistent":"false"
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
    
    
    
    
    
    
    
    
    
    
    
