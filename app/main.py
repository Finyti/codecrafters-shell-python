import sys
import os



def exitFunc(exitStatus):
    if(len(exitStatus) == 0 or int(exitStatus[0]) not in (0, 1)):
        exit(0)
    exit(int(exitStatus[0])) 




def echo(text):
    print(' '.join(text))
    return




def type(command, commandDict):
    # Check for builtin functions
    if(command in commandDict):
        print(f'{command} is a shell builtin')
        return
    
    # Check for executables in PATH
    paths=os.environ['PATH'].split(os.pathsep)
    for path in paths:
        if(not os.path.exists(path)):
            pass
        # Check if file path exist, and then whether or not it is executable
        if(os.path.exists(path+f"/{command}")):
            if(os.access(path+f"/{command}", os.X_OK)):
                print(f'{command} is {path}/{command}')
                return
    print(f'{command}: not found')




def main():
    while(True):
        sys.stdout.write("$ ")
        commandDict = {'exit': exitFunc,
                       'echo': echo,
                       'type': type}

        userInput = input()
        userInputSplit = userInput.split()
    

        # Handles each individual command or exceptions. 
        # If cases are used because each individual command may have need of different atributes 

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