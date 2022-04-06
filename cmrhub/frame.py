with open("/usr/enable_mkuser","r") as fd:
    line = " The Code is: '"+fd.read().strip()+"' "
    print()
    print("+","-"*len(line),"+",sep='')
    print("|",line,"|",sep='')
    print("+","-"*len(line),"+",sep='')
    print()
