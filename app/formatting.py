import sys
import os

def formatInput(userInput):

    """
    Accepts one variable. \n
    'userInput' - string of user input, that needs to be formatted \n

    Returns a list of arguments of the command. Supports single quotes.
    """

    # Function goes charachter by character

    # Array for all args (including command)
    formattedInput = ['']

    # Word index increments with starting of evaluation of a new arg. Is always the last existing index of formattedInput
    wordIndex = 0

    # Markers for functionality modification 
    singleQuoteMarker = False
    doubleQuoteMarker = False
    literalIteration = False
    for index, char in enumerate(userInput):
        # The order of if's here is important. Earlier if's catch certain cases which should not go through and to later if's

        # For cases when \ interprets next chat literally of some symbol 
        if(literalIteration == True):
                literalIteration = False
                formattedInput[wordIndex] = str(formattedInput[wordIndex]) + f'''{char}'''
                continue
        
        # Tackles 3 cases of \ functionality. 
        # 1. Outside quotes (normal \ functionality) 
        # 2. Double quotes (normal \ functionality when symbol in front of it is functional otherwise \ interpreted literally)
        # 3. Single quotes (\ interpreted literally)
        if(char == "\\") and not singleQuoteMarker and not doubleQuoteMarker:
            literalIteration = True
            continue
        elif(char == "\\" and doubleQuoteMarker):
            try:
                if(userInput[index+1] == '"' or userInput[index+1] == '\\'):
                    literalIteration = True
                    continue
                else:
                    formattedInput[wordIndex] = str(formattedInput[wordIndex]) + "\\"
            except:
                pass
            continue
        elif(char == "\\" and singleQuoteMarker):
            formattedInput[wordIndex] = str(formattedInput[wordIndex]) + "\\"
            continue

            
        # Support for quotes
        if char == "'" and not doubleQuoteMarker:
            singleQuoteMarker = not singleQuoteMarker
            continue
        elif singleQuoteMarker:
            formattedInput[wordIndex] = str(formattedInput[wordIndex]) + f'''{char}'''
            continue

        if char == '"' and not singleQuoteMarker:
            doubleQuoteMarker = not doubleQuoteMarker
            continue
        elif doubleQuoteMarker:
            formattedInput[wordIndex] = str(formattedInput[wordIndex]) + f'''{char}'''
            continue

        if(char == ">" and not singleQuoteMarker and not doubleQuoteMarker):
            if(index-1>=0):
                if(userInput[index-1] not in '123456789'):
                    formattedInput[wordIndex] = str(formattedInput[wordIndex]) + "1"

        # Starts new argument
        if char == " " and not singleQuoteMarker and not doubleQuoteMarker:
            if(formattedInput[-1] != ''):
                formattedInput.append('')
                wordIndex += 1
                continue
            else:
                continue


        # If nothing else was ticked, add a char to arg
        formattedInput[wordIndex] = str(formattedInput[wordIndex]) + f'''{char}'''


    # Clean up blanks:
    for arg in formattedInput:
        if(arg == ''):
            formattedInput.remove('')



    return formattedInput

# ['ls', ' 1>', '/home/leo/Desktop/testls2.txt', ' ', ' ', '']