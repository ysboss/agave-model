#!/bin/bash

export MPICH_HOME="${HOME}/${CONTAINER_VER}/mpich${MPICH_VER}"
export PATH=$MPICH_HOME/bin:$PATH
export LD_LIBRARY_PATH=$MPICH_HOME/bin:$LD_LIBRARY_PATH

if [ "$HYPRE_VER" = "" ]
then
   echo "Please specify the HYPRE version using $HYPRE_VER" 
   exit 2
fi
export HYPRE_HOME="${HOME}/${CONTAINER_VER}/hypre${HYPRE_VER}"
if [ ! -d ${HYPRE_HOME} ]
then
    #if [ "${BUILD}" != "yes" ]
    #then
    #    echo "Please do a build run"
    #fi
    mkdir -p $HOME/build
    cd $HOME/build
    if [ ! -r hypre-$HYPRE_VER.tar.gz ]
    then
      curl -kLO https://computation.llnl.gov/projects/hypre-scalable-linear-solvers-multigrid-methods/download/hypre-$HYPRE_VER.tar.gz
    fi
    rm -fr hypre-$HYPRE_VER
    tar xzf hypre-$HYPRE_VER.tar.gz
    cd hypre-$HYPRE_VER/src
    ./configure --prefix=${HYPRE_HOME} 
    make install 
    echo "export HYPRE_HOME=${HYPRE_HOME}" > env.sh
    echo "export PATH=$PATH:${HYPRE_HOME}/src" >> env.sh
    echo "export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${HYPRE_HOME}/lib" >> env.sh
    chmod 755 env.sh
    ./env.sh
fi
