export MPICH_HOME="${HOME}/${CONTAINER_VER}/mpich${MPICH_VER}"
export PATH=$PATH:$MPICH_HOME/bin

if [ "$H5_VER" != "" ]
then
    export H5_HOME="$HOME/${CONTAINER_VER}/dep-mpich${MPICH_VER}/h5-${H5_VER}"
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$H5_HOME/lib
fi
