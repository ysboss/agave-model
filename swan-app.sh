#!/bin/bash

# Save the current directory
echo $PWD
source ../.env
source ./env.sh #Contains: versions of software

export SPACK_ROOT=/build-dir/ubuntu_xenial/spack
source $SPACK_ROOT/share/spack/setup-env.sh

spack load swan@${SWAN_VER}

echo "Job is: $PBS_JOBID" 
echo "Mom is: $(hostname)"
echo "Running from $(pwd)"

#NP=$((${AGAVE_JOB_NODE_COUNT}*${AGAVE_JOB_PROCESSORS_PER_NODE}))
NP=$((${nx}*${ny}))
set -x
mpirun -np "$NP" -machinefile "$PBS_NODEFILE" swan
