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
#     spack install funwave
#
# You can edit this file again by typing:
#
#     spack edit funwave
#
# See the Spack documentation for more information on packaging.
# ----------------------------------------------------------------------------

from spack import *
import os

class Funwave(MakefilePackage):
    """
    What is FUNWAVE-TVD?
    FUNWAVE-TVD is the Total Variation Diminishing (TVD) version of the fully nonlinear Boussinesq wave model (FUNWAVE) developed by Shi et al. (2012). The FUNWAVE model was initially developed by Kirby et al. (1998) based on Wei et al. (1995). The development of the present version was motivated by recent needs for modeling of surfzone--cale optical properties in a Boussinesq model framework, and modeling of Tsunami waves in both a global/coastal scale for prediction of coastal inundation and a basin scale for wave propagation.
    """

    # FIXME: Add a proper url for your package's homepage here.
    homepage = "https://fengyanshi.github.io/build/html/index.html"
    url      = "file:///tarballs/FUNWAVE-2020.10.01.tgz"

    # FIXME: Add a list of GitHub accounts to
    # notify when the package is updated.
    # maintainers = ['github_user1', 'github_user2']

    version('3.2', git='https://github.com/fengyanshi/FUNWAVE-TVD', tag='v3.2')
    version('3.1', git='https://github.com/fengyanshi/FUNWAVE-TVD', tag='v3.1')
    version('3.0', git='https://github.com/fengyanshi/FUNWAVE-TVD', tag='v3.0')

    depends_on('mpi')

    # FIXME: Add dependencies if required.
    # depends_on('foo')
    parallel = False

    def build(self, spec, prefix):
        #env['FC'] = spec["mpi"].mpifc
        os.chdir('./src')
        make()

    def install(self, spec, prefix):
        bin = os.path.join(prefix,"bin")
        os.makedirs(bin, exist_ok=True)
        copy("./funwave_vessel",os.path.join(bin,"funwave"))

    def edit(self, spec, prefix):
        # FIXME: Edit the Makefile if necessary
        # FIXME: If not needed delete this function
        makefile = FileFilter('Makefile')
        #makefile.filter('CC = .*', 'CC = cc')
