from bs4 import BeautifulSoup
import requests, re, os
from command import cmd

mainurl = "http://swanmodel.sourceforge.net/download/download.htm"
g = re.match(r'(.*)/',mainurl)
baseurl = g.group(1)

r = requests.get(mainurl)
bs = BeautifulSoup(r.text,features='html5lib')

for a in bs.find_all('a', href=True):
    if a.get_text().strip() == 'here':
      url = baseurl+"/"+a["href"]
      print(url)
      g = re.search(r'swan(\d+)\.',a["href"])
      ver = int(g.group(1))
      print("Version:",ver)
      cmd("curl -kLO %s" % url)
      cmd("tar xzvf swan%d.tar.gz" % ver)
      os.chdir("swan%d" % ver)
      cmd("make config")
      cmd("make mpi")
      cmd("cp swan.exe /usr/local/bin")
      break
