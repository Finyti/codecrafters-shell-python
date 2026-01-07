import sys
import os

def redirect(output, file):
    try:
        if(os.path.exists(file)):
            with open(file, "w") as f:
                f.write(str(output))
        else:
            with open(file, 'x+') as f:
                f.write(str(output))
    except:
        print("Can't access directory: "+file)


def append(output, file):
    try:
        if(os.path.exists(file)):
            with open(file, "a") as f:
                if(output[-1] == '\n'):
                    output = output[:-1]
                if(os.path.getsize(file) == 0):
                    f.write(str(output))
                else:
                    f.write(str('\n' + output))
        else:
            with open(file, "a+") as f:
                f.write(str(output))
    except:
        print("Can't access directory: "+file)
