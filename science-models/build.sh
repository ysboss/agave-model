#!/bin/bash
if [ "${SPACK_ROOT}" == "" ]
then
  echo "SPACK_ROOT is not set"
  exit 2
fi
spack-init.sh
source $SPACK_ROOT/share/spack/setup-env.sh
for p in funwave nhwave openfoam delft3d
do
  #python3 /usr/local/bin/spack-reconfigure.py
  echo spack install $p $*
  spack install $p $*
done
echo spack install -j1 swan $*
spack install -j1 swan $*
#spack gc -y
