import sys
import os

def inCommandDict(command, commandDict):
    if(type(command) == list): 
        return str(command[0]) in commandDict
    return str(command) in commandDict

def isExec(command, commandPath = ""):
    """
    Accepts two variables. \n
    path - a sysytem path \n
    command - command to search in sysytem path \n

    Returns a True if command exist and is executable by provided path \n
    or False otherwise
    """
    if(commandPath != ""):
        if(os.access(commandPath+f"/{command}", os.X_OK)):
            return True
        else:
            return False
    else:
        paths=os.environ['PATH'].split(os.pathsep)
        for path in paths:
            if(path != ''):
                if(os.path.isfile(path+f"/{command}") and os.access(path+f"/{command}", os.X_OK)):
                    return True
    return False


def getExec(executive, paths=os.environ['PATH'].split(os.pathsep)):
    """
    Accepts two variables. \n
    'paths' - list of sysytem paths \n
    'exec' - command to search in sysytem paths \n \n

    If exec exists returns a touple with [0] being 'exec' name and [1] being valid path \n
    or None otherwise
    """
    for path in paths:
        if(path != ''):
            if(isExec(executive, path)):
                return (exec, path)
    return None


def separateCommands(fullCommand, commandDict, commandModificatorsDict):
    commandArray = []
    for element in fullCommand:
        try:
            if(element not in commandModificatorsDict):
                if commandArray[-1][0] == 'echo' or commandArray[-1][0] == 'type':
                    commandArray[-1].append(element)
                    continue
            elif element in commandModificatorsDict:
                commandArray.append([element])
                continue
        except:
            pass

        if inCommandDict(element, commandDict) or isExec(element):
            commandArray.append([element])
        else:
            successFlag = False
            try:
                if(len(commandArray) == 0):
                    commandArray.append([element])
                    successFlag = True
            except:
                pass
            else:
                if(not successFlag):
                    commandArray[-1].append(element)
    return commandArray
