from spack import *
import os
import re
from subprocess import Popen, PIPE
#from __future__ import print_function

class Delft3d(MakefilePackage):
     """FIXME: Put a proper description of your package here."""

     # FIXME: Add a proper url for your package's homepage here.
     homepage = "https://oss.deltares.nl/web/delft3d/home"
     # url      = "file:///build-dir/tarballs/delft3d-repository-65936.tgz"
     # url = "file:///home/chrispv/tarballs-temp/delft3d-6.5.396.tar.gz"
     url = "file:///tarballs/delft3d-6.5.3.tgz"

     # FIXME: Add a list of GitHub accounts to
     # notify when the package is updated.
     # maintainers = ['github_user1', 'github_user2']
     # FIXME: Add proper versions here.
     version('6.5.3', sha256='777d5f3d483c55b0e37dc4325b9df2e4a3dbb6100c5b93d4310bda361025ab3e')

     # FIXME: Add dependencies if required.
     #depends_on('subversion')
     depends_on('autoconf')
     depends_on('automake')
     depends_on('libtool')
     #depends_on('gcc')
     depends_on('mpi')
     depends_on('bison')
     #depends_on('expat')
     #depends_on('openssl')
     #depends_on('ruby')
     depends_on('netcdf-c')
     depends_on('netcdf-fortran')
     depends_on('metis')
     depends_on('petsc')
     depends_on('pkgconfig')

     parallel = False

     def build(self, spec, prefix):
        os.system("set -xe")

        os.environ["METIS"]=self.spec['metis'].prefix
        os.environ["NETF"]=self.spec['netcdf-fortran'].prefix
        os.environ["YACC"]=self.spec['bison'].prefix

        print(os.getcwd())
        print(os.listdir('.'))
        p_exe = Popen(['./autogen.sh'], cwd="src", stdout=PIPE, stderr=PIPE, universal_newlines=True)
        out, err = p_exe.communicate()
        print(out, err, end="")

        p_exe2 = Popen(["./autogen.sh"], cwd="src/third_party_open/kdtree2", stdout=PIPE, stderr=PIPE, universal_newlines=True)
        out, err = p_exe2.communicate()
        print(out, err, end="")

        os.environ["CLFLAG"]='-O2'
        os.environ["CXXFLAGS"]='-O2'
        os.environ["FFLAGS"]='-O2'
        os.environ["FCFLAGS"]="-O2 -I%s/include" % os.environ["NETF"]

        p_exe3 = Popen(["./configure", "--prefix=%s" % prefix, "--with-netcdf", "--with-mpi", "--with-metis=%s" % os.environ["METIS"], "--with-petsc"], cwd="src", stdout=PIPE, stderr=PIPE, universal_newlines=True)
        out, err = p_exe3.communicate()
        print(out, err, end="")

        with open("src/tools_gpl/Makefile", "r") as f:
           lines = f.readlines()
        with open("src/tools_gpl/Makefile", "w") as f:
           for line in lines:
              if "vs" not in line:
                 f.write(line)

        os.chdir("src")
        with open("utils_lgpl/nefis/packages/nefis/src/oc.c", "r") as fd:
            oc_s = fd.read()
        oc_s = re.sub(r'FILE_OPEN\(\s+file_name,\s+acType\s+\);',r'FILE_OPEN( file_name, acType, FILE_MODE );',oc_s)
        with open("utils_lgpl/nefis/packages/nefis/src/oc.c", "w") as fd:
            print(oc_s, file=fd, end='')
        make("ds-install")

     def install(self, spec, prefix):
        # FIXME: Unknown Build System
        p_exe = Popen(["./libtool_install.sh"], cwd="%s/bin" % prefix, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        out, err = p_exe.communicate()
        print(out, err, end="")
        p_exe1 = Popen(["./clean.sh"], stdout=PIPE, stderr=PIPE, universal_newlines=True)
        out, err = p_exe1.communicate()
        print(out, err, end="")
