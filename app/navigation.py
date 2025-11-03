import sys
import os

def pwd(currentDirectory):
    print(currentDirectory)
    return

def cd(newPath, wokingDirectory):
    if('~' in newPath):
        newPath = os.getenv('HOME')
    elif('../' in newPath):
        stepsBack = len(newPath.split('../')) - 1
        wokingDirectoryElements = wokingDirectory.split(os.path.sep)
        if(stepsBack < len(wokingDirectoryElements) -1):
            newPath = os.path.sep.join(wokingDirectoryElements[:len(wokingDirectoryElements)-stepsBack])
        else:
            newPath = os.path.sep
        return newPath
    elif('./' in newPath):
        if(wokingDirectory[-1] != '/'):
            newPath = wokingDirectory+newPath[1:]
        else:
            newPath = wokingDirectory+newPath[2:]
    if(os.path.exists(newPath)):
        return newPath
    else:
        print(f'cd: {newPath}: No such file or directory')
        return
