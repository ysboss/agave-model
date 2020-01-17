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
source hypre.sh

# Apps
source nhwave.sh

export NHWAVE_DIR=$INSTALL_DIR/NHWAVE-${NHWAVE_VER}

# Restore the current directory
cd $HERE

echo "Job is: $PBS_JOBID"
echo "Mom is: $(hostname)"
echo "Running from $(pwd)"

NP=$((${nx}*${ny}))
perl -p -i -e "s/^[ \t]*PX[ \t]*=[ \t]*\d+[ \t]*$/PX=$nx/" input.txt
perl -p -i -e "s/^[ \t]*PY[ \t]*=[ \t]*\d+[ \t]*$/PY=$ny/" input.txt
mpirun -np "${NP}" -machinefile "$PBS_NODEFILE" $NHWAVE_DIR/src/nhwave
