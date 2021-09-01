#!/bin/bash
if [ "${SPACK_ROOT}" == "" ]
then
  echo "SPACK_ROOT is not set"
  exit 2
fi
spack-init.sh
source $SPACK_ROOT/share/spack/setup-env.sh
for p in funwave nhwave swan openfoam delft3d
do
  python3 /usr/local/bin/spack-reconfigure.py
  spack install $p $*
done
spack install swan@4.1.2.1
spack gc -y
