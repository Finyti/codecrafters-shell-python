import sys


def main():

    sys.stdout.write("$ ")
    userInput = input()
    commandList = {}
    if(str(userInput) not in commandList):
        sys.stdout.write(f'{userInput}: command not found')


if __name__ == "__main__":
    main()
