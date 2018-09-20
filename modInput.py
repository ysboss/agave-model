import re

# Compute a complete list of prime factors
def factorize(n):
    factors = []
    while n % 2 == 0:
        n //= 2
        factors += [2]
    f = 1
    while n != 1:
        f += 2
        while n % f == 0:
            n //= f
            factors += [f]
    return factors

# Construct px and py from the factors
# in the factors array in order to try
# and get the most square boxes possible
# for each MPI process to work on.
# The pair nx, ny describes the total
# computational domain.
def bestf(i,px,py,factors,nx,ny):
    if i < len(factors):
        f = factors[i]
        rat1,px1,py1 = bestf(i+1,px*f,py,factors,nx,ny)
        rat2,px2,py2 = bestf(i+1,px,py*f,factors,nx,ny)
        if rat2 < rat1:
            return rat2,px2,py2
        else:
            return rat1,px1,py1
    else:
        rat1 = nx/px
        rat2 = ny/py
        return max(rat1/rat2,rat2/rat1),px,py

# Modify input. The first argument is the total number
# of processes. The second is a file name. ModInput
# will use bestf to re-write the number of processes
# in the input.txt file (the PX and PY parameters).
def modInput(n,fname):
    factors = factorize(n)
    with open(fname,"r") as fd:
        contents = fd.read()
    g = re.search(r'^Mglob\s*=\s*(\d+)',contents,re.MULTILINE)
    if g:
        ny = int(g.group(1))
    g = re.search(r'^Nglob\s*=\s*(\d+)',contents,re.MULTILINE)
    if g:
        nx = int(g.group(1))
    r,px,py = bestf(0,1,1,factors,nx,ny)
    contents = re.sub(r'(\n|^)PX\s*=\s*(\d+)',r'\1PX = %d' % px,contents,re.MULTILINE)
    contents = re.sub(r'(\n|^)PY\s*=\s*(\d+)',r'\1PY = %d' % py,contents,re.MULTILINE)
    with open(fname,"w") as fd:
        fd.write(contents)
    return px,py

# Demonstration and test.
if __name__ == "__main__":
    print(modInput(256*27,"input.txt"))
