#!/bin/bash
if [ "$H5_VER" = "" ]
then
   echo "Please specify the H5 version using H5_VER" 
   exit 2
fi
export H5_HOME="$HOME/${CONTAINER_VER}/dep-mpich${MPICH_VER}/h5-${H5_VER}"
if [ ! -d $H5_HOME ]
then
  mkdir -p $HOME/build
  cd $HOME/build
  A=$(echo $H5_VER|cut -d. -f1)
  B=$(echo $H5_VER|cut -d. -f2)
  C=$(echo $H5_VER|cut -d. -f3)
  export H5_MIN_VER="$A.$B"
  export H5_MAJ_VER="$A.$B.$C"
  curl -kLO https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-$H5_MIN_VER/hdf5-$H5_MAJ_VER/src/hdf5-$H5_MAJ_VER.tar.gz
  tar xzf hdf5-$H5_MAJ_VER.tar.gz
  cd hdf5-$H5_MAJ_VER
  export CC="$MPICH_HOME/bin/mpicc"
  export CXX="$MPICH_HOME/bin/mpicxx"
  ./configure --enable-fortran --enable-shared --enable-parallel --prefix=$H5_HOME
  make install -j ${PROCS}
  echo "export H5_HOME=${H5_HOME}" > env.sh
  echo 'export PATH=${H5_HOME}/bin:$PATH' >> env.sh
  echo 'export LD_LIBRARY_PATH=${H5_HOME}/lib' >> env.sh
fi
