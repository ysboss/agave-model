#!/bin/bash
if [ "$SPACK_ROOT" = "" ]
then
  echo SPACK_ROOT is not set >&2
  exit 1
fi
mkdir -p $SPACK_ROOT
if [ ! -w "$SPACK_ROOT" ]
then
  echo "'$SPACK_ROOT' is not writable" >&2
  exit 2
fi
if [ ! -d $SPACK_ROOT/.git ]
then
  git clone https://github.com/spack/spack.git ${SPACK_ROOT}
fi

grep spack/setup-env.sh ~/.bashrc > /dev/null 2>&1
if [ $? != 0 ]
then
  echo "source ${SPACK_ROOT}/share/spack/setup-env.sh" >> ~/.bashrc
  source ${SPACK_ROOT}/share/spack/setup-env.sh
fi

mkdir -p ~/.spack
if [ ! -r ~/.spack/packages.yaml ]
then
  cp /usr/local/packages.yaml ~/.spack/packages.yaml
fi
spack external find xz tar pkgconf findutils diffutils perl

for p in funwave nhwave swan
do
  mkdir -p $SPACK_ROOT/var/spack/repos/builtin/packages/$p
  cp /packages/$p/package.py $SPACK_ROOT/var/spack/repos/builtin/packages/$p/package.py
done
