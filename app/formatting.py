import sys
import os

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
    doubleQuoteMarker = False

    literalIteration = False
    for index, char in enumerate(userInput):

        if(literalIteration == True):
                literalIteration = False
                formattedInput[wordIndex] = str(formattedInput[wordIndex]) + f'''{char}'''
                continue
        
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

        if char == " " and not singleQuoteMarker and not doubleQuoteMarker:
            if(formattedInput[-1] != ''):
                formattedInput.append('')
                wordIndex += 1
        else:
            formattedInput[wordIndex] = str(formattedInput[wordIndex]) + f'''{char}'''
    return formattedInput

