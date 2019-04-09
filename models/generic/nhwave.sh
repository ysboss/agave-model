#!/bin/bash

source /usr/local/bin/env.sh 

export HYPRE_HOME="${HOME}/${CONTAINER_VER}/hypre${HYPRE_VER}"

if [ "$NHWAVE_VER" != "" ]
then
    export NHWAVE_VER="$NHWAVE_VER"
    echo "BUILDING NHWAVE: Version $NHWAVE_VER"

    # download swan source code and extract it 
    export BASE_DIR="$HOME/$CONTAINER_VER/nhwave$NHWAVE_VER"
    mkdir -p $BASE_DIR
    cd $BASE_DIR
    #curl -kLO http://downloads.sourceforge.net/project/swanmodel/swan/${SWAN_V1}.${SWAN_V2}/swan${SWAN_VER}.tar.gz
    git clone https://github.com/JimKirby/NHWAVE.git
    #tar xzf swan${SWAN_VER}.tar.gz

    # compile swan 
    cd NHWAVE/src
    mv Makefile.supermic.mpif90 Makefile
    sed -i 's/DEF_FLAGS     = -P -C -traditional/            DEF_FLAGS     = -P -traditional/' Makefile
    sed -i 's/FLAG_9 = -DINTEL/      #       FLAG_9 = -DINTEL/' Makefile
    sed -i 's/FLAG_15 = -DFROUDE_CAP/      #       FLAG_15 = -DFROUDE_CAP/' Makefile
    sed -i 's/LIBS  = -L\/worka\/work\/chzhang\/hypre\/parallel\/lib -lHYPRE/      LIBS  = -L${HYPRE_HOME}\/lib -lHYPRE/' Makefile
    sed -i 's/INCS  = -L\/worka\/work\/chzhang\/hypre\/parallel\/include/      INCS  = -I${HYPRE_HOME}\/include/' Makefile
   
    echo "BUILDING HERE:"
    pwd
    make clean && make 
fi
