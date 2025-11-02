import sys

def exitFunc(exitStatus):
    if(int(exitStatus[0]) not in (0, 1)):
        exit(0)
    exit(int(exitStatus[0])) 


def main():

    while(True):
        sys.stdout.write("$ ")
        commandList = {'exit': exitFunc}

        userInput = input()

        userInputSplit = userInput.split()
    
        if(str(userInputSplit[0]) not in commandList):
            sys.stdout.write(f'{userInput}: command not found' + '\n')
        else:
            commandList[userInputSplit[0]](userInputSplit[1:])



if __name__ == "__main__":
    main()