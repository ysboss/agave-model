import requests, re, os
from command import cmd

import json
jsonurl = "https://sourceforge.net/projects/swanmodel/best_release.json"
r = requests.get(jsonurl)
jd = json.loads(r.text)
url = jd["platform_releases"]["linux"]["url"]
filename = jd["platform_releases"]["linux"]["filename"]
ftar = re.sub(r'.*/','',filename)
fbase = re.sub(r'.tar.gz$','',ftar)

cmd("curl -kL %s -o %s" % (url,fbase))
cmd("tar xzvf %s" % fbase)
os.chdir(fbase)
cmd("make config")
cmd("make mpi")
cmd("cp swan.exe /usr/local/bin")
