if [ "$MPICH_VER" = "" ]
then
   echo "Please specify the MPICH version using MPICH_VER" 
   exit 2
fi
export MPICH_HOME="${HOME}/${CONTAINER_VER}/mpich${MPICH_VER}"
if [ ! -x "${MPICH_HOME}/bin/mpirun" ]
then
    if [ "${BUILD}" != "yes" ]
    then
        echo "Please do a build run"
    fi
    mkdir -p $HOME/build
    cd $HOME/build
    if [ ! -r mpich-$MPICH_VER.tar.gz ]
    then
      curl -kLO http://www.mpich.org/static/downloads/$MPICH_VER/mpich-$MPICH_VER.tar.gz
    fi
    rm -fr mpich-$MPICH_VER
    tar xzf mpich-$MPICH_VER.tar.gz
    cd mpich-$MPICH_VER
    ./configure --prefix=${MPICH_HOME}
    make install -j $PROCS
    echo "export MPICH_HOME=${MPICH_HOME}" > env.sh
    echo "export PATH=${MPICH_HOME}/bin:${PATH}" >> env.sh
    echo "export LD_LIBRARY_PATH=${MPICH_HOME}/lib:${LD_LIBRARY_PATH}" >> env.sh
    chmod 755 env.sh 
    ./env.sh
fi
