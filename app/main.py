import sys

def exitFunc(exitStatus):
    if(len(exitStatus) == 0 or int(exitStatus[0]) not in (0, 1)):
        exit(0)
    exit(int(exitStatus[0])) 

def echo(text):
    print(' '.join(text))
    return

def type(command, commandDict):
    if(command in commandDict):
        print(f'{command} is a shell builtin')
    else:
        print(f'{command}: not found')

def main():

    while(True):
        sys.stdout.write("$ ")
        commandDict = {'exit': exitFunc,
                       'echo': echo,
                       'type': type}

        userInput = input()

        userInputSplit = userInput.split()
    
        if(str(userInputSplit[0]) not in commandDict):
            sys.stdout.write(f'{userInput}: command not found' + '\n')
        if(userInputSplit[0] == 'exit'):
            commandDict[userInputSplit[0]](userInputSplit[1:])
        if(userInputSplit[0] == 'echo'):
            commandDict[userInputSplit[0]](userInputSplit[1:])
        if(userInputSplit[0] == 'type'):
            commandDict[userInputSplit[0]](userInputSplit[1], commandDict)



if __name__ == "__main__":
    main()