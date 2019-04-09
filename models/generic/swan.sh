#!/bin/bash

source /usr/local/bin/env.sh

if [ "$SWAN_V1" != "" ]
then
    if [ "$SWAN_V2" = "" ]
    then
        echo 'Please set the $SWAN_V2 variable'
        exit 2
    fi
    export SWAN_VER="${SWAN_V1}${SWAN_V2}"
    echo "BUILDING SWAN: Version $SWAN_VER"
    # download swan source code and extract it 
    export BASE_DIR="$HOME/$CONTAINER_VER/dep-mpich$MPICH_VER"
    export SWAN_DIR="$HOME/$CONTAINER_VER/dep-mpich$MPICH_VER/swan${SWAN_VER}"
    mkdir -p $BASE_DIR
    cd $BASE_DIR
    if [ ! -r swan${SWAN_VER}.tar.gz ]
    then
        curl -kLO http://downloads.sourceforge.net/project/swanmodel/swan/${SWAN_V1}.${SWAN_V2}/swan${SWAN_VER}.tar.gz
    fi
    rm -fr swan${SWAN_VER}
    tar xzf swan${SWAN_VER}.tar.gz

    # compile swan 
    cd swan${SWAN_VER}
    echo "BUILDING HERE:"
    pwd
    make config && make mpi

    chmod 755 $SWAN_DIR/swanrun 
fi
