if [ -z "$CMR_OPTS" ]
then
    echo "Please configure CMR_OPTS in your ~/.bashrc"
    echo "Here is an example:"
    echo "CMR_OPTS=\"--bind /work"
    echo "       --bind /scratch"
    echo "       --bind /var/spool"
    echo "       --bind /etc/ssh/ssh_known_hosts\""
    echo
fi

if [ -z "$CMR_IMAGE" ]
then
    echo The CMR_IMAGE variable is not set. It should
    echo be set in your ~/.bashrc and should be built from
    echo docker://stevenrbrandt/spack-cmr-built
    echo
fi

if [ -z "$SPACK_CMR_ROOT" ]
then
    echo The SPACK_CMR_ROOT variable is not set. Please set
    echo it to the location where you would like to have
    echo spack installed.
    echo
fi

if [ -z "$CMR_DATA_DIR" ]
then
    echo The CMR_DATA_DIR needs to be set to a
    echo place where the CMR can store files.
    echo e.g. $HOME/cmr-data-dir/
    echo
fi
if [ -d /spack ]
then
    # We are in the CMR
    
    if [ "$SPACK_CMR_ROOT" = "" ]
    then
        export SPACK_ROOT=/spack
        export "Warning: Please set the Spack CMR root or you won't be able to install new Spack packages"
    else
        export SPACK_ROOT="$SPACK_CMR_ROOT"
        if [ ! -d "$SPACK_ROOT" ]
        then
            echo "Cloning Spack..."
            git clone --depth 1 --single-branch --branch v0.17.1 https://github.com/spack/spack.git "$SPACK_ROOT"
            echo 'Adding Default Models to Spack...'
            cp -r /packages/* $SPACK_ROOT/var/spack/repos/builtin/packages/
        fi
    fi

    source "$SPACK_ROOT/share/spack/setup-env.sh"

    SPACK_FIND=no
    export SPACK_USER_CONFIG_PATH=$HOME/.spack-cmr
    if [ ! -d "$SPACK_USER_CONFIG_PATH" ]
    then
        # create spack directory
        SPACK_FIND=yes
        echo "Setting up the CMR..."
        mkdir -p "$SPACK_USER_CONFIG_PATH"
    fi
    if [ ! -e "$SPACK_USER_CONFIG_PATH/upstreams.yaml" ]
    then
        cat > "$SPACK_USER_CONFIG_PATH/upstreams.yaml" << EOF
upstreams:
  spack-instance-1:
    install_tree: /spack/opt/spack
    modules:
      tcl: /spack/share/spack/modules
EOF
    fi
    if [ ! -e "$SPACK_USER_CONFIG_PATH/packages.yaml" ]
    then
        cat > "$SPACK_USER_CONFIG_PATH/packages.yaml" << EOF
packages:
  all:
    compiler: [gcc]
    providers:
      mpi:
      - mpich
      - openmpi
EOF
    fi
    if [ "$SPACK_FIND" = "yes" ]
    then
        spack compiler find
        spack external find perl diffutils findutils
    fi
fi
