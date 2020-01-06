import os
class safe_reader:
    def __init__(self, fname):
        self.fd = os.open(fname, os.O_RDONLY)
        self.buf = b''
        self.ready = True
        self.index = 0
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        os.close(self.fd)
    def read(self):
        s = ''
        for line in self.readlines():
            s += line
        return s
    def readlines(self):
        s = ''
        while self.ready:
            if self.index >= len(self.buf):
                self.buf = os.read(self.fd, 1024)
                self.index = 0
                if len(self.buf) == 0:
                    self.ready = False
                    break
            k = self.buf[self.index]
            c = chr(k)
            s += c
            self.index += 1
            if c == '\n':
                yield s
                s = ''
