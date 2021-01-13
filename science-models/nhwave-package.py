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
#     spack install nhwave
#
# You can edit this file again by typing:
#
#     spack edit nhwave
#
# See the Spack documentation for more information on packaging.
# ----------------------------------------------------------------------------

from spack import *
import os
from subprocess import call
import re

def make_makefile():
    with open("Makefile", "w") as fw:
      print("""
#-----------BEGIN MAKEFILE-------------------------------------------------
         SHELL         = /bin/sh
         DEF_FLAGS     = -P -traditional
         EXEC          = nhwave
#==========================================================================
#--------------------------------------------------------------------------
#        PRECISION          DEFAULT PRECISION: SINGLE                     
#                           UNCOMMENT TO SELECT DOUBLE PRECISION
#--------------------------------------------------------------------------
         FLAG_1 = -DDOUBLE_PRECISION
         FLAG_2 = -DPARALLEL
#        FLAG_3 = -DLANDSLIDE
#         FLAG_4 = -DSALINITY
#         FLAG_5 = -DTEMPERATURE
#         FLAG_6 = -DBUBBLE
#         FLAG_7 = -DSEDIMENT
#         FLAG_8 = -DVEGETATION
#         FLAG_9 = -DINTEL
#         FLAG_10 = -DBALANCE2D
#	      FLAG_11 = -DOBSTACLE
#	      FLAG_12 = -DTWOLAYERSLIDE
#	      FLAG_13 = -DCORALREEF
#	      FLAG_14 = -DPOROUSMEDIA
         FLAG_15 = -DFROUDE_CAP
#         FLAG_16 = -DCOUPLING
#         FLAG_17 = -DFLUIDSLIDE
#         FLAG_18 = -DLANDSLIDE_COMPREHENSIVE
#         FLAG_19 = -DDEFORMABLESLIDE
#--------------------------------------------------------------------------
#  mpi defs 
#--------------------------------------------------------------------------
         CPP      = /usr/bin/cpp
         CPPFLAGS = $(DEF_FLAGS)
#         FC       = ifort
         FC        = mpif90
         DEBFLGS  = 
         OPT      = #-g
         CLIB     = 
#==========================================================================
         FFLAGS = $(DEBFLGS) $(OPT) 
         MDEPFLAGS = --cpp --fext=f90 --file=-
         RANLIB = ranlib
#--------------------------------------------------------------------------
#  CAT Preprocessing Flags
#--------------------------------------------------------------------------
         CPPARGS = $(CPPFLAGS) $(DEF_FLAGS) $(FLAG_1) $(FLAG_2) $(FLAG_3) \
                   $(FLAG_4) $(FLAG_5) $(FLAG_6) $(FLAG_7) $(FLAG_8) $(FLAG_9) \
	           $(FLAG_10) $(FLAG_11) $(FLAG_12) $(FLAG_13) $(FLAG_14) \
			   $(FLAG_15) $(FLAG_16) $(FLAG_17) $(FLAG_18) $(FLAG_19)
#--------------------------------------------------------------------------
#  Libraries           
#--------------------------------------------------------------------------
         LIBS  = -L$(HYPRE_DIR)/lib -lHYPRE
         INCS  = -L$(HYPRE_DIR)/include
#--------------------------------------------------------------------------
#  Preprocessing and Compilation Directives
#--------------------------------------------------------------------------
.SUFFIXES: .o .f90 .F .F90 

.F.o:
	$(CPP) $(CPPARGS) $*.F > $*.f90
	$(FC)  -c $(FFLAGS) $(INCS) $*.f90
#	\rm $*.f90
#--------------------------------------------------------------------------
#  NHWAVE Source Code.
#--------------------------------------------------------------------------

MODS  = mod_global.F mod_util.F 

MAIN  = nhwave.F initialize.F two_layer_slide.F fluid_slide.F

SRCS = $(MODS)  $(MAIN)

OBJS = $(SRCS:.F=.o) nspcg.o

#--------------------------------------------------------------------------
#  Linking Directives               
#--------------------------------------------------------------------------

$(EXEC):	$(OBJS)
		$(FC) $(FFLAGS) $(LDFLAGS) -o $(EXEC) $(OBJS) $(LIBS)
#--------------------------------------------------------------------------
#  Cleaning targets.
#--------------------------------------------------------------------------

clean:
		/bin/rm -f *.o *.mod

clobber:	clean
		/bin/rm -f *.f90 *.o nhwave
""",file=fw)


class Nhwave(MakefilePackage):
    """
    NHWAVE is a three-dimensional shock-capturing Non-Hydrostatic WAVE model developed by Ma et al. (2012), which solves the incompressible Navier-Stokes equations in terrain and surface-following sigma coordinates.
    """

    # FIXME: Add a proper url for your package's homepage here.
    homepage = "https://sites.google.com/site/gangfma/nhwave"
    url      = "file:///tarballs/NHWAVE-2020.10.10.tgz"

    # FIXME: Add a list of GitHub accounts to
    # notify when the package is updated.
    # maintainers = ['github_user1', 'github_user2']

    version('3.0', git='https://github.com/JimKirby/NHWAVE.git', tag='V3.0')

    # FIXME: Add dependencies if required.
    depends_on('mpi')
    depends_on('hypre')



    parallel = False

    def build(self, spec, prefix):
        os.chdir('src')
        lib_dir = os.path.dirname(spec["hypre"].libs[0])
        base_dir = os.path.dirname(lib_dir)
        print("HYPRE_DIR:",base_dir)
        os.environ["HYPRE_DIR"] = base_dir
        make_makefile()
        make()
        os.chdir('..')

    def install(self, spec, prefix):
        bin = os.path.join(prefix,"bin")
        os.makedirs(bin, exist_ok=True)
        copy("src/nhwave",os.path.join(bin,"nhwave"))
