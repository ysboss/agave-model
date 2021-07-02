#!/bin/bash

# Save the current directory
echo $PWD
source ../.env
source ./env.sh #Contains: versions of software
source $SPACK_ROOT/share/spack/setup-env.sh

# Should be set already in bashrc
# see QBC bashrc
#export SPACK_ROOT=/build-dir/ubuntu_xenial/spack

model_w_ver=${model^^}
model_w_ver+="_VER"

spack load ${model}@${!model_w_ver}
spack load mpich@${MPICH_VER}

echo "Job is: $PBS_JOBID" 
echo "Mom is: $(hostname)"
echo "Running from $(pwd)"

#NP=$((${AGAVE_JOB_NODE_COUNT}*${AGAVE_JOB_PROCESSORS_PER_NODE}))

# JSON File Location: /build_dir/json_files
# Should be named model-version.json

# get from JSON (Need to ask Prof)
NP=$((${nx}*${ny}*${nz}))
set -x

#get from json (Need to ask Prof about parsing and reading json file in bash)
#source /build-dir/json/${model}-$model_ver}.json

#if test -f input.txt; then
#    perl -p -i -e "s/^[ \t]*PX[ \t]*=[ \t]*\d+[ \t]*$/PX=$nx/" input.txt
#    perl -p -i -e "s/^[ \t]*PY[ \t]*=[ \t]*\d+[ \t]*$/PY=$ny/" input.txt
#fi

mpirun -np "${NP}" ${model}
