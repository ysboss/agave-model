#!/bin/bash

source /usr/local/bin/env.sh

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
fi
