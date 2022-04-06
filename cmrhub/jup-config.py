import os
from traceback import print_exc
from subprocess import Popen, PIPE

def call(cmd, inp=None):
    print("Calling:",cmd)
    if inp is None:
        p = Popen(cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    else:
        p = Popen(cmd, stdout=PIPE, stderr=PIPE, stdin=PIPE, universal_newlines=True)
    out, err = p.communicate(inp)
    print(out,end='',flush=True)
    print(err,end='',flush=True)

c.JupyterHub.authenticator_class = 'cyolauthenticator.CYOLAuthenticator'
c.JupyterHub.template_paths = ['/jinja/templates']

# openssl genrsa -out rootCA.key 2048
# openssl req -x509 -new -nodes -key rootCA.key -sha256 -days 1024 -out rootCA.pem

certname = os.environ.get('CERT_NAME','tutorial')
cer = f'/etc/pki/tls/certs/{certname}.cer'
key = f'/etc/pki/tls/private/{certname}.key'

try:

  if not os.path.exists(key):
    os.makedirs(os.path.dirname(key), exist_ok=True)
    call(["openssl","genrsa","-out",key,"2048"])

  if not os.path.exists(cer):
    os.makedirs(os.path.dirname(cer), exist_ok=True)
    answers = open("info.txt").read()
    call(["openssl","req","-x509","-new","-nodes","-key",key,"-sha256","-days","1024","-out",cer],answers)

  if os.path.exists(cer) and os.path.exists(key):
    print("Starting with SSL")
    c.JupyterHub.ssl_cert = cer
    c.JupyterHub.ssl_key =  key
  else:
    print("Starting without SSL")


  # Uncomment if needed
  #c.JupyterHub.base_url = '/somename/'
except:
  print_exc()
print(" >>> CONFIGURATION COMPLETE <<<<")
