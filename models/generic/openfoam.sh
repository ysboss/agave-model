#!/bin/bash

source /usr/local/bin/env.sh

if [ "$OPENFOAM_VER" != "" ]
then
    echo "BUILDING OPENFOAM: Version $OPENFOAM_VER"
    export BASE_DIR="$HOME/dep-mpich$MPICH_VER"
    mkdir -p $BASE_DIR
    cd $BASE_DIR
    curl -kLO https://sourceforge.net/projects/openfoamplus/files/v${OPENFOAM_VER}/OpenFOAM-v${OPENFOAM_VER}.tgz
    curl -kLO https://sourceforge.net/projects/openfoamplus/files/v${OPENFOAM_VER}/ThirdParty-v${OPENFOAM_VER}.tgz
    tar xzf OpenFOAM-v${OPENFOAM_VER}.tgz
    tar xzf ThirdParty-v${OPENFOAM_VER}.tgz
    export OPENFOAM_DIR=$BASE_DIR/OpenFOAM-v${OPENFOAM_VER}
    export SHELL=/bin/bash
    PROCS=$(lscpu | grep CPU.s.: | head -1 | cut -d: -f2)
    export WM_NCOMPPROCS=$(($PROCS/2))
    cd $OPENFOAM_DIR
    source etc/bashrc
    export WM_THIRD_PARTY_DIR=$BASE_DIR/ThirdParty-v${OPENFOAM_VER}

    # Change the compiler from g++ to mpicxx
    export WM_CC=mpicc
    export WM_CXX=mpicxx
    perl -p -i -e 's/^export WM_CC=/#$&/m' etc/config.sh/settings
    perl -p -i -e 's/^export WM_CXX=/#$&/m' etc/config.sh/settings
    for f in wmake/rules/*/c++
    do
      perl -p -i -e 's/\bg\+\+/\${WM_CXX}/' $f
    done

    source etc/bashrc

    # Make it possible to pass other options to mpirun
    # using environment variable MPI_OPTS
    perl -p -i -e 's/mpirun -np .nProcs/$& \$MPI_OPTS/' $WM_PROJECT_DIR/bin/tools/RunFunctions
    foamSystemCheck
    ./Allwmake -j 2>&1 | tee make.out
fi
