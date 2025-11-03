import sys
import os

def inCommandDict(command, commandDict):
    if(type(command) == list): 
        return str(command[0]) in commandDict
    return str(command) in commandDict

def GetAllFilePaths(paths, command):
    validPaths = []
    for path in paths:
        if(not os.path.exists(path)):
            pass
        # Check if file path exist, and then whether or not it is executable
        if(os.path.exists(path+f"/{command}")):
            validPaths.append(path)
    return validPaths

def isExec(path, command):
    if(os.access(path+f"/{command}", os.X_OK)):
        return True
    else:
        return False


def getExec(paths, command):
    for path in paths:
        if(path != ''):
            if(isExec(path, command)):
                return (command, path)
    return None


def exitFunc(exitStatus):
    if(len(exitStatus) == 0 or int(exitStatus[0]) not in (0, 1)):
        exit(0)
    exit(int(exitStatus[0])) 




def echo(text):
    print(' '.join(text))
    return



def typeOfArgument(command, commandDict={}):
    # Check for builtin functions
    if(inCommandDict(command, commandDict)):
        print(f'{command} is a shell builtin')
        return
    
    paths=os.environ['PATH'].split(os.pathsep)
    
    # Check if file path exist, and then whether or not it is executable
    # validPaths = GetAllFilePaths(paths, command)
    validExec = getExec(paths, command)
    if(validExec != None):
        return (command, validExec[1])

    print(f'{command}: not found')
    return



def execute(fullCommand, args):

    if(fullCommand[0] == '.'):
        fullCommand = fullCommand[1:]
    path = ''
    command = ''

    # if givven command preceeded by full path
    if(os.path.sep in fullCommand):
        path = fullCommand.split(os.path.sep)[:-1]
        path = os.path.sep.join(path)
        command = fullCommand.split(os.path.sep)[-1]
    # if givven only the command
    else:
        command = fullCommand
        # paths=os.environ['PATH'].split(os.pathsep)
        paths=os.environ['PATH'].split(os.pathsep)
        execValidity = getExec(paths, command)
        if(execValidity != None):
            path = execValidity[1]
    if(path != '' and isExec(path, command)):
        os.system(f'{command} {" ".join(args)}')
        return True
    return False
        
    


def main():
    while(True):
        sys.stdout.write("$ ")
        commandDict = {'exit': exitFunc,
                       'echo': echo,
                       'type': typeOfArgument,
                       'execute': execute}

        userInput = input()
        userInputSplit = userInput.split()
    

        # Handles each individual command or exceptions. 
        # If cases are used because each individual command may have need of different atributes 

        if(not inCommandDict(userInputSplit, commandDict)):
            isExecuted = commandDict['execute'](userInputSplit[0], userInputSplit[1:])
            if(not isExecuted):
                sys.stdout.write(f'{userInput}: command not found' + '\n')
        if(userInputSplit[0] == 'exit'):
            commandDict[userInputSplit[0]](userInputSplit[1:])
        if(userInputSplit[0] == 'echo'):
            commandDict[userInputSplit[0]](userInputSplit[1:])
        if(userInputSplit[0] == 'type'):
            typeReturn = commandDict[userInputSplit[0]](userInputSplit[1], commandDict)
            if(typeReturn != None):
                print(f'{typeReturn[0]} is {typeReturn[1]}/{typeReturn[0]}')






if __name__ == "__main__":
    main()