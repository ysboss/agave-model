#!/bin/bash
if [ "${SPACK_ROOT}" == "" ]
then
  echo "SPACK_ROOT is not set"
  exit 2
fi
spack-init.sh
source $SPACK_ROOT/share/spack/setup-env.sh
for p in funwave nhwave swan openfoam
do
  spack install $p target=x86_64
done
spack gc -y
