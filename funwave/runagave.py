from time import sleep
from setvar import *
import os

def runagavecmd(cmd,infile=None):
    setvar("REMOTE_COMMAND="+cmd)
    # The input file is an optional parameter, both
    # to our function and to the Agave application.
    if infile == None:
        setvar("INPUTS={}")
    else:
        setvar('INPUTS={"datafile":"'+infile+'"}')
    setvar("JOB_FILE=job-remote-$PID.txt")
    # Create the Json for the job file.
    writefile("$JOB_FILE","""
 {
   "name":"fork-command-1",
   "appId": "${AGAVE_USERNAME}-${MACHINE_NAME}-fork-1.0",
   "executionSystem": "${EXEC_MACHINE}",
   "archive": false,
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
    }
   ],
   "parameters": {
     "command":"${REMOTE_COMMAND}"
   },
   "inputs":${INPUTS}
 }""")
    # Run the job and capture the output.
    setvar("""
# Capture the output of the job submit command
OUTPUT=$(jobs-submit -F $JOB_FILE)
# Parse out the job id from the output
JOB_ID=$(echo $OUTPUT | cut -d' ' -f4)
""")
    # Poll and wait for the job to finish.
    for iter in range(80): # Excessively generous
        setvar("STAT=$(jobs-status $JOB_ID)")
        stat = os.environ["STAT"]
        sleep(5.0)
        if stat == "FINISHED" or stat == "FAILED":
            break
    # Fetch the job output from the remote machine
    setvar("CMD=jobs-output-get ${JOB_ID} fork-command-1.out")
    os.system(os.environ["CMD"])
    print("All done! Output follows.")
    # Load the output into memory
    output=readfile("fork-command-1.out")
    print("=" * 70)
    print(output)

def runagavequeue(image_name,exe_name,par_file):
    setvar("PAR_FILE="+par_file)
    setvar("IMAGE_NAME="+image_name)
    setvar("EXE_NAME="+exe_name)
    setvar("JOB_FILE=job-remote-$PID.txt")
    # Create the Json for the job file.
    writefile("$JOB_FILE","""
 {
   "name":"queue-command-1",
   "appId": "${AGAVE_USERNAME}-${MACHINE_NAME}-queue-1.0",
   "executionSystem": "${EXEC_MACHINE}-HPC",
   "archive": false,
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
    }
   ],
   "parameters": {
     "exe_name":"${EXE_NAME}",
     "image_name":"${IMAGE_NAME}"
   },
   "inputs":{
     "par_file":"${PAR_FILE}"
   }
 }""")
    # Run the job and capture the output.
    setvar("""
# Capture the output of the job submit command
OUTPUT=$(jobs-submit -F $JOB_FILE)
# Parse out the job id from the output
JOB_ID=$(echo $OUTPUT | cut -d' ' -f4)
""")
    # Poll and wait for the job to finish.
    for iter in range(80): # Excessively generous
        setvar("STAT=$(jobs-status $JOB_ID)")
        stat = os.environ["STAT"]
        sleep(5.0)
        if stat == "FINISHED" or stat == "FAILED":
            break
    # Fetch the job output from the remote machine
    setvar("CMD=jobs-output-get ${JOB_ID} queue-command-1-${JOB_ID}.out")
    os.system(os.environ["CMD"])
    print("All done! Output follows.")
    # Load the output into memory
    output=readfile("queue-command-1-${JOB_ID}.out")
    print("=" * 70)
    print(output)
