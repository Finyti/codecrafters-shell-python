import sys
import os

def pwd(currentDirectory):
    print(currentDirectory)
    return

def cd(newPath):
    if(os.path.exists(newPath)):
        return newPath
    else:
        print(f'cd: {newPath}: No such file or directory')
        return
