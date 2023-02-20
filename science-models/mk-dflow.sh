source $SPACK_ROOT/share/spack/setup-env.sh
spack clean
spack env create dflowfm
spack env activate dflowfm
spack config add concretizer:reuse:true
spack config add concretizer:unify:true
spack config add packages:all:require:target=x86_64
spack add cmake intel-oneapi-compilers@2022.1.0 libxml2 metis netcdf-c parmetis patchelf diffutils@3.6%gcc hwloc%oneapi netcdf-c gdal@2.4.2%gcc+python openblas%gcc mpich%oneapi netcdf-fortran%oneapi petsc%oneapi proj@4.9.2%oneapi~tiff pkg-config@0.28 
spack add dflowfm%oneapi target=x86_64
spack install --fail-fast
