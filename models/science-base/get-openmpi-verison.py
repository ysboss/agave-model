import requests
import bs4
import os, sys, re
from subprocess import call

result = requests.get("https://www.open-mpi.org/software")

g = re.search(r'/(v\d+\.\d+)',result.url)
if g:
  v1 = g.group(1)
  print("version:",g.group(1))

download_url = None
bresult = bs4.BeautifulSoup(result.text,features='html5lib')
for a in bresult.find_all('a', href=True):
    url = a["href"]
    g = re.match(r'https://download.open-mpi.org/release/open-mpi/'+v1+r'/openmpi-([\d\.]+).tar.gz',url)
    if g:
      v2 = g.group(1)
      download_url = g.group(0)
      break

call(["curl","-kLO",download_url])
call(["tar","xzvf","openmpi-{v2}.tar.gz".format(v2=v2)])
os.chdir("openmpi-"+v2)
call(["./configure"])
call(["make","-j","10","install"])
os.chdir("/home")
call(["rm","-fr","openmpi-{v2}".format(v2=v2)])
call(["rm","-f","openmpi-{v2}.tar.gz".format(v2=v2)])
