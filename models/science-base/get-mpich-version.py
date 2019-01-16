import requests
import bs4
import os, sys, re
from subprocess import call

result = requests.get("http://www.mpich.org/downloads/")

bresult = bs4.BeautifulSoup(result.text,features='html5lib')
for a in bresult.find_all('a', href=True):
    if a.text == "http":
       url = a["href"]
       g = re.match(r'^http://www.mpich.org/static/downloads/(.*)/(mpich-(.*)).tar.gz$',url)
       if g:
           ver = g.group(1)
           fname = g.group(2)
           download_url = url
           print("Version:",ver)
           break
       else:
           raise Exception("Unexpected link")

call(["curl","-kLO",download_url])
call(["tar","xzf",fname+".tar.gz"])
os.chdir(fname)
call(["./configure"])
call(["make","-j","10","install"])
os.chdir("..")
call(["rm","-fr",fname])
call(["rm","-fr",fname+".tar.gz"])
#os.chdir("/home")
#call(["rm","-fr","openmpi-{v2}".format(v2=v2)])
#call(["rm","-f","openmpi-{v2}.tar.gz".format(v2=v2)])
