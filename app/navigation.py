import sys
import os

class NavigationModule:
    def pwd(parent):
        return str(parent.workingDirectory).encode("UTF-8")

    def cd(parent, newPath):
        if('~' in newPath):
            if('/' in newPath):
                newPath = os.getenv('HOME')+newPath[1:]
            else:
                newPath = os.getenv('HOME')
        elif('../' in newPath):
            stepsBack = len(newPath.split('../')) - 1
            wokingDirectoryElements = parent.workingDirectory.split(os.path.sep)
            if(stepsBack < len(wokingDirectoryElements) -1):
                newPath = os.path.sep.join(wokingDirectoryElements[:len(wokingDirectoryElements)-stepsBack])
            else:
                newPath = os.path.sep
            parent.addStdFeedback("", "")
            if (newPath != None):
                parent.workingDirectory = newPath
            return
        elif('./' in newPath):
            if(parent.workingDirectory[-1] != '/'):
                newPath = parent.workingDirectory+newPath[1:]
            else:
                newPath = parent.workingDirectory+newPath[2:]
        if(os.path.exists(newPath)):
            parent.addStdFeedback("", "")
            if (newPath != None):
                parent.workingDirectory = newPath
            return
        else:
            # print(f'Error cd: {newPath}: No such file or directory')
            parent.addStdFeedback("", f'cd: {newPath}: No such file or directory\n')

        
