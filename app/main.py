import sys
import os
import app.navigation as navigation

def inCommandDict(command, commandDict):
    if(type(command) == list): 
        return str(command[0]) in commandDict
    return str(command) in commandDict


def exitFunc(exitStatus):
    if(len(exitStatus) == 0 or int(exitStatus[0]) not in (0, 1)):
        exit(0)
    exit(int(exitStatus[0])) 

def echo(text):
    print(' '.join(text))
    return


def GetAllFilePaths(paths, file):
    """
    Accepts two variables. \n
    paths - list of sysytem paths \n
    file - file to search in sysytem paths \n

    Returns a List of all paths where a file was found
    """
    validPaths = []
    for path in paths:
        if(not os.path.exists(path)):
            pass
        # Check if file path exist, and then whether or not it is executable
        if(os.path.exists(path+f"/{file}")):
            validPaths.append(path)
    return validPaths

def isExec(path, command):
    """
    Accepts two variables. \n
    path - a sysytem path \n
    command - command to search in sysytem path \n

    Returns a True if command exist and is executable by provided path \n
    or False otherwise
    """
    if(os.access(path+f"/{command}", os.X_OK)):
        return True
    else:
        return False


def getExec(paths, exec):
    """
    Accepts two variables. \n
    'paths' - list of sysytem paths \n
    'exec' - command to search in sysytem paths \n \n

    If exec exists returns a touple with [0] being 'exec' name and [1] being valid path \n
    or None otherwise
    """
    for path in paths:
        if(path != ''):
            if(isExec(path, exec)):
                return (exec, path)
    return None




def typeOfArgument(command, commandDict):
    """
    Accepts two variables. \n
    'command' - command to check \n
    'commandDict' - Dictionary with all builtin commands \n \n

    If command is an executable, returns a touple with [0] being 'command' name and [1] being valid path \n
    or None in any other case
    """
    # Check if command is a builtin functions
    if(inCommandDict(command, commandDict)):
        print(f'{command} is a shell builtin')
        return
    
    # If not builtin, check if command is a an executable accesible in any of the locations in PATH
    paths=os.environ['PATH'].split(os.pathsep)
    validExec = getExec(paths, command)
    if(validExec != None):
        print(f'{command} is {validExec[1]}/{command}')
        return (command, validExec[1])

    print(f'{command}: not found')
    return



def execute(fullCommand, args):
    """
    Accepts two variables. \n
    'fullCommand' - string of user input, may contain full execx path, or just the name \n
    'args' - List of arguments to be passed when executing the command \n \n

    If command is an executable, executes it with given arguments
    Returns True if execution happened, False otherwise
    """
    path = ''
    command = ''

    if(fullCommand[0] == '.'):
        fullCommand = fullCommand[1:]

    # if givven command preceeded by full path
    if(os.path.sep in fullCommand):
        path = fullCommand.split(os.path.sep)[:-1]
        path = os.path.sep.join(path)
        command = fullCommand.split(os.path.sep)[-1]
    # if givven only the command name
    else:
        command = fullCommand
        paths=os.environ['PATH'].split(os.pathsep)
        validExec = getExec(paths, command)
        if(validExec != None):
            path = validExec[1]
    # First format the string for passing the arguments, then execute the whole command
    if(path != '' and isExec(path, command)):
        argsString = ""
        for arg in args:
            argsString += f"'{arg}' "
        os.system(f'{command} {argsString}')
        return True
    return False
        

def formatInput(userInput):

    """
    Accepts one variable. \n
    'userInput' - string of user input, that needs to be formatted \n

    Returns a list of arguments of the command. Supports single quotes.
    """

    # Goes charachter by character

    formattedInput = ['']

    wordIndex = 0
    singleQuoteMarker = False
    for char in userInput:
        if char == "'":
            singleQuoteMarker = not singleQuoteMarker
            continue
        elif singleQuoteMarker:
            formattedInput[wordIndex] = str(formattedInput[wordIndex]) + str(char)
            continue

        if char == " " and not singleQuoteMarker:
            if(formattedInput[-1] != ''):
                formattedInput.append('')
                wordIndex += 1
        else:
            formattedInput[wordIndex] = str(formattedInput[wordIndex]) + str(char)


    return formattedInput


def main():

    wokingDirectory = os.path.abspath("")
    while(True):
        sys.stdout.write("$ ")
        commandDict = {'exit': exitFunc,
                       'echo': echo,
                       'type': typeOfArgument,
                       'execute': execute,
                       'pwd': navigation.pwd,
                       'cd': navigation.cd}

        userInput = input()
        userInputSplit = formatInput(userInput)
    

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
            commandDict[userInputSplit[0]](userInputSplit[1], commandDict)
        if(userInputSplit[0] == 'pwd'):
            commandDict[userInputSplit[0]](wokingDirectory)
        if(userInputSplit[0] == 'cd'):
            if(len(userInputSplit) > 1):
                newPath = commandDict[userInputSplit[0]](userInputSplit[1], wokingDirectory)
            else:
                newPath = os.path.abspath("")
            if (newPath != None):
                wokingDirectory = newPath






if __name__ == "__main__":
    main()