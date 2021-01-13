# Copyright 2013-2020 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

# ----------------------------------------------------------------------------
# If you submit this package back to Spack as a pull request,
# please first remove this boilerplate and all FIXME comments.
#
# This is a template package file for Spack.  We've put "FIXME"
# next to all the things you'll want to change. Once you've handled
# them, you can save this file and test your package like this:
#
#     spack install swan
#
# You can edit this file again by typing:
#
#     spack edit swan
#
# See the Spack documentation for more information on packaging.
# ----------------------------------------------------------------------------

from spack import *
import os


class Swan(MakefilePackage):
    """
    SWAN is a third-generation wave model, developed at Delft University of Technology, that computes random, short-crested wind-generated waves in coastal regions and inland waters.
    """

    # FIXME: Add a proper url for your package's homepage here.
    homepage = "https://www.tudelft.nl/en/ceg/about-faculty/departments/hydraulic-engineering/sections/environmental-fluid-mechanics/research/swan/"
    url      = "file:///tarballs/swan-4.1.3.1.tgz"

    # FIXME: Add a list of GitHub accounts to
    # notify when the package is updated.
    # maintainers = ['github_user1', 'github_user2']

    version('4.1.3.1', sha256='83d1b55d3e264fc4bec47cdd6aba41b919f9986b6b7f14923327b9c7a65750fc')

    # FIXME: Add dependencies if required.
    depends_on('mpi')

    parallel = False

    def build(self, spec, prefix):
        os.environ["EXTO"]="o"
        os.environ["F90_MPI"]=spec["mpi"].mpifc
        os.environ["FLAGS90_MSC"]="-ffree-line-length-0"
        os.environ["OUT"]="-o"
        os.environ["F90_SER"]="gfortran"
        make("mpi")

    def edit(self, spec, prefix):
        # FIXME: Edit the Makefile if necessary
        # FIXME: If not needed delete this function
        makefile = FileFilter('Makefile')
        # makefile.filter('CC = .*', 'CC = cc')

    def install(self, spec, prefix):
        bin = os.path.join(prefix,"bin")
        os.makedirs(bin, exist_ok=True)
        copy("swan.exe",os.path.join(bin,"swan"))
