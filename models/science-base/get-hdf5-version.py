import requests
import bs4
import os, sys, re
from subprocess import call

#result = requests.get("https://www.hdfgroup.org/downloads/hdf5/source-code/")

#bresult = bs4.BeautifulSoup(result.text,features='html5lib')
#for a in bresult.find_all('a', onclick=True):
#    onclick = a["onclick"]
#    g = re.match(r"this.href='(.*)'",onclick)
#    if g and re.search(r'-zip-',onclick):
#        url = g.group(1)
#        print(a.text, url)
#        break

url = "https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-1.6/hdf5-1.6.10/src/hdf5-1.6.10.tar.gz"

call(["curl","-kL",url,"-o","hdf5.tar.gz"])
call(["tar","xzf","hdf5.tar.gz"])
for fname in os.listdir():
  g = re.match(r'hdf5-([\d\.-]+)$',fname)
  if g:
    ver = g.group(1)
    print(fname,"VER:",ver)
    break

call(["mkdir","-p","build-hdf5"])
os.chdir("build-hdf5")
os.environ["CC"]="/usr/local/bin/mpicc"
call(["../"+fname+"/configure","--enable-fortran","--enable-shared","--enable-parallel"])
call(["make","-j","10","install"])
os.chdir("..")
#call(["rm","-fr",fname])
#call(["rm","-fr","hdf5.zip"])
#call(["rm","-fr","build-hdf5"])
