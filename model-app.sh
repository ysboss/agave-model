#!/bin/bash

# Save the current directory
echo $PWD
source ../.env
source ./env.sh #Contains: versions of software

export SPACK_ROOT=/build-dir/ubuntu_xenial/spack
source $SPACK_ROOT/share/spack/setup-env.sh

# model_dependencies='spack dependencies ${model}@${model_version}'
model_w_ver=${model^^}
model_w_ver+="_VER"

spack load ${model}@${!model_w_ver}
spack find > dependencies-info.txt

echo "Job is: $PBS_JOBID" 
echo "Mom is: $(hostname)"
echo "Running from $(pwd)"

#NP=$((${AGAVE_JOB_NODE_COUNT}*${AGAVE_JOB_PROCESSORS_PER_NODE}))
NP=$((${nx}*${ny}))
set -x

if test -f input.txt; then
    perl -p -i -e "s/^[ \t]*PX[ \t]*=[ \t]*\d+[ \t]*$/PX=$nx/" input.txt
    perl -p -i -e "s/^[ \t]*PY[ \t]*=[ \t]*\d+[ \t]*$/PY=$ny/" input.txt
fi

mpirun -np "${NP}" -machinefile "$PBS_NODEFILE" ${model}
