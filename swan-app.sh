#!/bin/bash

# Save the current directory
HERE=$PWD
source ../.env
source ./env.sh
export NO_BUILD=yes

export BUILD_DIR=/build-dir/$OS_VER
export INSTALL_DIR=/install-dir/$OS_VER

mkdir -p $BUILD_DIR
mkdir -p $INSTALL_DIR

# Foundation
source mpich.sh

# Apps
source swan.sh

export SWAN_DIR=$PWD/swan${SWAN_VER}

# Restore the current directory
cd $HERE

echo "Job is: $PBS_JOBID" 
echo "Mom is: $(hostname)"
echo "Running from $(pwd)"

#NP=$((${AGAVE_JOB_NODE_COUNT}*${AGAVE_JOB_PROCESSORS_PER_NODE}))
NP=$((${nx}*${ny}))
set -x
mpirun -np "$NP" -machinefile "$PBS_NODEFILE" $SWAN_DIR/swan.exe
