import input_params

def write_env():
    print("Writing run_dir/env.sh...")
    with open("run_dir/env.sh","w") as fd:
        print("export MPICH_VER=%s" % input_params.get('mpich-ver'),file=fd)
        print("export HYPRE_VER=%s" % input_params.get('hypre-ver'),file=fd)
        print("export HDF5_VER=%s" % input_params.get('hdf5-ver'),file=fd)
        model = value=input_params.get('title').lower()
        print("export model="+model,file=fd)
        swan_ver = input_params.get("modelversion_swan")
        if swan_ver is not None:
            print("export SWAN_VER=%s" % swan_ver,file=fd)
        funwave_ver = input_params.get("modelversion_funwave_tvd")
        if funwave_ver is not None:
            print("export FUNWAVE_VER=%s" % funwave_ver,file=fd)
        openfoam_ver = input_params.get("modelversion_openfoam")
        if openfoam_ver is not None:
            print("export OPENFOAM_VER=%s" % openfoam_ver,file=fd)
        nhwave_ver = input_params.get("modelversion_nhwave")
        if nhwave_ver is not None:
            print("export NHWAVE_VER=%s" % nhwave_ver,file=fd)
