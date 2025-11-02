import sys


def main():
    while(True):
        sys.stdout.write("$ ")
        commandList = {}

        userInput = input()

        if(str(userInput) not in commandList):
            sys.stdout.write(f'{userInput}: command not found' + '\n')


if __name__ == "__main__":
    main()
