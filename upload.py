import io
import os
import re
from IPython.display import display
import fileupload

upload_widget = fileupload.FileUploadWidget()

finput = None

def set_input(n):
    global finput
    finput = n

def upload():

    def _cb(change):
        global finput
        filename = change['owner'].filename
        data = change['owner'].data
        fd = os.open(filename,os.O_CREAT|os.O_WRONLY)
        os.write(fd,data)
        os.close(fd)
        finput.value = filename

    upload_widget.observe(_cb, names='data')
    display(upload_widget)

upload()


#test webhook
#test webhook2
