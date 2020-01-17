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
source funwave.sh

# Restore the current directory
cd $HERE

echo "Job is: $PBS_JOBID"
echo "Mom is: $(hostname)"
echo "Running from $(pwd)"
echo "Running version $FUNWAVE_VER"

NP=$((${nx}*${ny}))
perl -p -i -e "s/^[ \t]*PX[ \t]*=[ \t]*\d+[ \t]*$/PX=$nx/" input.txt
perl -p -i -e "s/^[ \t]*PY[ \t]*=[ \t]*\d+[ \t]*$/PY=$ny/" input.txt
mpirun -np "${NP}" -machinefile "$PBS_NODEFILE" $FUNWAVE_DIR/funwave-work/funwave-*-gnu-parallel-single
