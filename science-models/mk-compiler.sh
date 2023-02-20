source $SPACK_ROOT/share/spack/setup-env.sh
export LANG=en_US.UTF-8
spack install --fail-fast intel-oneapi-compilers@2022.1.0 target=x86_64
spack load intel-oneapi-compilers
spack compiler find
