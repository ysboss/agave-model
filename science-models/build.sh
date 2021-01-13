#!/bin/bash
export SPACK_ROOT=/spack
spack-init.sh
source $SPACK_ROOT/share/spack/setup-env.sh
for p in funwave nhwave swan openfoam
do
  spack install $p
done
