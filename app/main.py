import sys
import os
import subprocess

import readline

import app.navigation as navigation
import app.formatting as formatting
import app.helpers as helpers
import app.redirection as redirection

"""
TODO:
1. Add command object (input is sepparated in preparation for execusion).
Add support for ';' and && as separators between commands.
Allow executing multiple commands per prompt. 
Store each command separetly in a Comand object type.


Another thing is command separation. For example right now
ls echo will print result of ls and empty echo. It should give
errors about not having directory echo. The command separation'
need to be per-comand with forst as a core, args evaluated differently.
(command; args)


This all lead to next objective:
2. Add per-comand output handling.
Input -> processing -> Commands -> execute = output -> command -> memory object
Command object has a flag inputRedirection to indicate whether or not it
should be printed. 
3. Add support for multiline:
A \
b \
C \
Can be done at the moment of input submision.
When no more bacwards slashed at the end,
combine all lines together in a command
object.


"""


class Memory:
    def __init__(self):
        pass
    def store(self):
        pass
    def load(self):
        pass

class Shell:

    def __init__(self):
        self.workingDirectory = os.path.abspath("")
        self.userInput = ''

        self.commandDict = {'exit': self.Command.exitFunc,
            'echo': self.Command.echo,
            'type': self.Command.typeOfArgument,
            # 'execute': self.execute,
            'pwd': self.Command.pwd,
            'cd': self.Command.cd}
        
        self.commandModificatorsDict = {'1>': redirection.redirect,
                                        '2>': redirection.redirect,
                                        '1>>': redirection.append,
                                        '2>>': redirection.append,
                                        '|': None}

        self.outputList = []
        self.errList = []
        self.outRedirectFlag = False
        self.errRedirectFlag = False

        self.pipeActive = False

        self.completeFound = False
        self.tabCount = 0
        self.doubleTabList = []
        
    class Command:
        def __init__(self, shell, command, isSub=False):
            self.shell = shell
            # command must be list
            self.isSub = isSub
            self.input = None

            self.fullCommand = command

            self.redirectionFlag = False
            self.redirectionSymbol = ''
            self.redirectionTarget = ''
            
            self.subCommands = []

            self.bytesOutput = None
            self.strOutput = None
            self.strErr = None


            if('|' in self.fullCommand):
                if any(True for x in self.fullCommand if x == '|' and type(x) == helpers.SpecialSymbol):
                    self.createSubdivision()

            fileRedirectors = list(self.shell.commandModificatorsDict.keys()).copy()
            fileRedirectors.remove("|")
            if(any(True for x in fileRedirectors if x in self.fullCommand)):
                self.cleanRedirects(fileRedirectors)

            # self.printSubdivisions()


        def __str__(self):
            return (f'fullCommand: {self.fullCommand} redirectionFlag: {self.redirectionFlag} redirectionSymbol: {self.redirectionSymbol} redirectionTarget: {self.redirectionTarget} isSub: {self.isSub}')
        
        def setFullCommand(self, newCommand):
            self.fullCommand = newCommand
        def getFullCommand(self):
            return self.fullCommand

        def toggleRedirection(self):
            self.redirectionFlag = not self.redirectionFlag

        def createSubdivision(self):
            '''
                Split comand into subcomands based on |
            '''
            cutList = []
            for el in self.fullCommand:
                if len(cutList) == 0:
                    cutList.append([])
                if(el == '|' and type(el) == helpers.SpecialSymbol):
                    cutList.append([])
                    continue
                cutList[-1].append(el)
            for index, el in enumerate(cutList):
                self.subCommands.append(self.shell.Command(self.shell, el, True))
                if(len(cutList)-1>index):
                    if(self.subCommands[-1].redirectionFlag == False):
                        self.subCommands[-1].redirectionFlag = True
                        self.subCommands[-1].redirectionSymbol = '|'
                    
        def printSubdivisions(self):
            if(len(self.subCommands) == 0):
                return
            for subComm in self.subCommands:
                print(subComm)
        def cleanRedirects(self, fileRedirectors):
            '''
            remove redirect flags from command and set right redirect symbol, target

            '''

            if(len(self.subCommands) > 0):
                return
            symbol = ''
            i = 0
            while(i < len(self.fullCommand)):
                command = self.fullCommand
                if(command[i] in fileRedirectors and type(command[i]) == helpers.SpecialSymbol):
                    symbol = command[i]
                    self.fullCommand.pop(i)

                    if(len(self.fullCommand)-1<i):
                        break
                    self.redirectionTarget = command[i]
                    self.fullCommand.pop(i)            # indexing shifted by one, so again removed at i
                    i = i-1
                i += 1


            self.redirectionFlag = True
            self.redirectionSymbol = str(symbol)


        def updateStd(self, stdObject):
            self.bytesOutput = stdObject
            self.strOutput = self.bytesOutput.stdout
            self.strOutput = self.bytesOutput.stderr

#  --------------------------------------------------
#    SIMPLE BUILTINS

        def exitFunc(self, exitStatus = 0):
            if(len(exitStatus) == 0 or int(exitStatus[0]) not in (0, 1)):
                exit(0)
            exit(int(exitStatus[0])) 

        def echo(self, text):
            # self.addStdFeedback(' '.join(text), "")
            output = subprocess.CompletedProcess(text, 0, str(' '.join(text)).encode("UTF-8"), ''.encode("UTF-8"))
            return output

        def typeOfArgument(self, commands):
            """
            Accepts two variables. \n
            'command' - command to check \n
            'commandDict' - Dictionary with all builtin commands \n \n

            If command is an executable, returns a touple with [0] being 'command' name and [1] being valid path \n
            or None in any other case
            """
            # Check if command is a builtin functions
            output = subprocess.CompletedProcess(commands, 0, ''.encode("UTF-8")), ''.encode("UTF-8")
            for command in commands:
                if(helpers.inCommandDict(command, self.commandDict)):
                    # print(f'{command} is a shell builtin')
                    output.stdout = (output.stdout.decode("UTF-8") + "\n" + str(f'{command} is a shell builtin')).encode("UTF-8")
                    continue
                
                # If not builtin, check if command is a an executable accesible in any of the locations in PATH
                validExec = helpers.getExec(command)
                if(validExec != None):
                    # print(f'{command} is {validExec[1]}/{command}')
                    output.stdout = (output.stdout.decode("UTF-8") + "\n" + str(f'{command} is {validExec[1]}/{command}')).encode("UTF-8")
                    continue
                
                output.stderr = (output.stderr.decode("UTF-8") + "\n" + str(f'{command}: not found')).encode("UTF-8")
            return output

        def pwd(self, command):
            output = subprocess.CompletedProcess(command, 0, str(self.shell.workingDirectory).encode("UTF-8"), ''.encode("UTF-8"))
            return output
        def cd(self, command):
            output = subprocess.CompletedProcess(command, 0, ''.encode("UTF-8"), ''.encode("UTF-8"))
            if(len(command) > 1):
                output.stderr = 'cd: too many arguments'.encode("UTF-8")
            else:
                navigation.NavigationModule.cd(self.shell, "".join(command))
            return output

#  --------------------------------------------------
#    COMMAND EXECUTION

        def runBuiltin(self, fullCommand, input=None, capture_output = True):
            # print("Execute builtin")
            output = None
            if(input!=None):
                output = self.shell.commandDict(fullCommand[0])(input)
            else:
                if(len(fullCommand) > 1):
                    output = self.shell.commandDict[fullCommand[0]](self, fullCommand[1:])
                else:
                    output = self.shell.commandDict[fullCommand[0]](self, '')
            if(capture_output == True):
                return output

        def run(self, fullCommand, input = None):
            output = None
            if(helpers.inCommandDict(fullCommand[0], self.shell.commandDict)):
                if(input == None):
                    output = self.runBuiltin(fullCommand, capture_output = True)
                else:
                    output = self.runBuiltin(fullCommand, input=input, capture_output = True)
            elif(helpers.isExec(fullCommand[0])):
                if(input == None):
                    output = subprocess.run(fullCommand, cwd=self.shell.workingDirectory, capture_output = True)
                else:
                    output = subprocess.run(fullCommand, cwd=self.shell.workingDirectory, input=input, capture_output = True)
            return output

        def executeCommand(self):

            # TODO add back the support for '\n' and "\n"
            # TODO print all results (outputs and errors)
            # TODO commit and merge with main. Test

            if(len(self.subCommands) > 0):
                for i, subCommand in enumerate(self.subCommands):
                    if(not helpers.inCommandDict(subCommand.fullCommand[0], self.shell.commandDict) and
                       not helpers.isExec(subCommand.fullCommand[0])):
                        sys.stdout.write(f'{' '.join(self.fullCommand)}: command not found' + '\n')
                    else:
                        output = None
                        
                        output = self.run(subCommand.fullCommand, subCommand.input)

                        subCommand.bytesOutput = output
                        subCommand.strErr = output.stderr.decode("UTF-8")
                        subCommand.strOutput = output.stdout.decode("UTF-8")

                        # print(subCommand.fullCommand, subCommand.strOutput)

                        
                        if(subCommand.redirectionFlag == True):
                            fileRedirectors = list(self.shell.commandModificatorsDict.keys()).copy()
                            fileRedirectors.remove("|")
                            if(subCommand.redirectionSymbol in fileRedirectors):
                                # TODO implemet redirections
                                if(subCommand.redirectionSymbol == '1>'):
                                    redirection.redirect(subCommand.strOutput, subCommand.redirectionTarget)
                                elif(subCommand.redirectionSymbol == '2>'):
                                    redirection.redirect(subCommand.strErr, subCommand.redirectionTarget)
                                elif(subCommand.redirectionSymbol == '1>>'):
                                    redirection.append(subCommand.strOutput, subCommand.redirectionTarget)
                                elif(subCommand.redirectionSymbol == '2>>'):
                                    redirection.append(subCommand.strErr, subCommand.redirectionTarget)
                                subCommand.bytesOutput = None
                                subCommand.strErr = None
                                subCommand.strOutput = None
                            elif(subCommand.redirectionSymbol == '|'):
                                if(len(self.subCommands) - 1 > i):
                                    self.subCommands[i+1].input = subCommand.bytesOutput.stdout
                                subCommand.bytesOutput = None
                                subCommand.strErr = None
                                subCommand.strOutput = None
                        elif(len(self.subCommands) - 1 == i and subCommand.redirectionFlag == False):
                            self.bytesOutput = subCommand.bytesOutput
                            self.strErr = subCommand.strErr
                            self.strOutput = subCommand.strOutput

            else:
                if(not helpers.inCommandDict(self.fullCommand[0], self.shell.commandDict) and
                not helpers.isExec(self.fullCommand[0])):
                    sys.stdout.write(f'{' '.join(self.fullCommand)}: command not found' + '\n')
                else:
                    output = self.run(self.fullCommand, self.input)

                    self.bytesOutput = output
                    self.strErr = output.stderr.decode("UTF-8")
                    self.strOutput = output.stdout.decode("UTF-8")

                    if(self.redirectionFlag == True):
                        # TODO implemet redirections
                        if(self.redirectionSymbol == '1>'):
                            print(self.redirectionTarget)
                            redirection.redirect(self.strOutput, self.redirectionTarget)
                        elif(self.redirectionSymbol == '2>'):
                            redirection.redirect(self.strErr, self.redirectionTarget)
                        elif(self.redirectionSymbol == '1>>'):
                            redirection.append(self.strOutput, self.redirectionTarget)
                        elif(self.redirectionSymbol == '2>>'):
                            redirection.append(self.strErr, self.redirectionTarget)
                        self.bytesOutput = None
                        self.strErr = None
                        self.strOutput = None



    #  --------------------------------------------------
#    DEALS WITH EXECUTABLES

    def createCommandObjects(self, separatedCommands):
        commandObjList = []
        for command in  separatedCommands:
            commandObjList.append(self.Command(self, command))

        return commandObjList



    def execute(self, fullCommand):
        # commandList = helpers.separateCommands(fullCommand, self.commandDict, self.commandModificatorsDict)
        commandList = helpers.separateCommands(fullCommand, self.commandDict, self.commandModificatorsDict)

        # print(f'execute: {commandList}')
        commandObjectsList = self.createCommandObjects(commandList)

        for command in commandObjectsList:
            command.executeCommand()
        for command in commandObjectsList:
            if(command.strErr != ''):
                sys.stdout.write(command.strErr  + '\n')
            else:
                sys.stdout.write(command.strOutput + '\n')





   #  --------------------------------------------------
#    DEALS WITH OUTPUTS AND ERROR_OUTPUTS

    def addStdFeedback(self, output, err):
        # if(output!=''):
        #     print(output)
        if(not isinstance(output, bytes)):
            output = output.encode("utf-8")
        if(not isinstance(err, bytes)):
            err = err.encode("utf-8")
        if(err.decode("utf-8")!='' and not self.errRedirectFlag):
            if(err[-1] != '\n'):
                sys.stdout.write(err.decode("utf-8") + '\n')
            else:
                sys.stdout.write(err.decode("utf-8"))
            # (Resets the loop instead of returning to wherever)
        self.outputList.append(output)
        self.errList.append(err)

    def printStdOut(self):
        if(len(self.outputList) == 0):
            return
        for index, output in enumerate(self.outputList):
            if(len(output.decode("utf-8")) == 0):
                return
            if(index == len(self.outputList)-1 and output[-1] == '\n'):
                sys.stdout.write(output.decode("utf-8")[0:-1])
            elif(index < len(self.outputList)-1 and output[-1] != '\n'):
                sys.stdout.write(output.decode("utf-8") + '\n')
            else:
                sys.stdout.write(output.decode("utf-8"))
        sys.stdout.write('\n')



   #  --------------------------------------------------
#   AUTOCOMPLETION

    def readlineSet(self):
        readline.parse_and_bind('set editing-mode vi') 
        readline.set_completer(self.complete)

        # Delims are needed to prevent to select autocomplete object.
        # Default is '-', but many comands use it.
        # I set it as ' ' (no need for spliting string)
        delims = readline.get_completer_delims()
        delims = delims.replace('-', '')
        readline.set_completer_delims(delims)

        # Detect libedit vs GNU readline
        doc = readline.__doc__ or ""
        if "libedit" in doc:
            # libedit-style binding (MacOS, BSD)
            readline.parse_and_bind("bind ^I rl_complete")
        else:
            # GNU readline-style binding (Most linux distrois)
            readline.parse_and_bind("tab: complete")



    def complete(self, string, state):

        # The readline calls complete on tab press untill it returns None, with state being +1 of previous call
        # The idea is to return all autocomplete options through returns and then None.
        # This list of options can then be printed when double tapping. 
        # Sadly, because of codecrafters tester and my inability to modify default
        # options printing I had to resolve to use complete as an event handler
        # of tab press. Logic of func does not allow state to go over 2.
        # That would allow default double tab behavior to occur


        # Self expanitory 
        if(string == ''):
            return None


        if(state == 0):
            self.tabCount +=1
            self.completeFound = False


        # If the singular autocomplete option is chosen (state is 1 if the completeFound is True)
        if(self.completeFound):
            print('\x07', end='', flush=True)
            return None
        
        # Manually lists all autocomplete options 
        if(self.tabCount == 2):
            print('\n' + "  ".join(self.doubleTabList))
            self.doubleTabList = []
            self.tabCount = 0
            buffer = readline.get_line_buffer()
            print("$ " + buffer, end="", flush=True)
            return None
        

        # Const options is alphabetically sorted autocomplete options that start with the string
        # Results is alphabetically autocomplete options that contain string

        const_options = list(self.commandDict.keys()) + helpers.getAllExec(os.environ['PATH'].split(os.pathsep))
        const_options = list(dict.fromkeys(const_options))
        results = []
        for key in const_options:
            if string in key:
                results.append(key)
        results = sorted(results)
        const_options = sorted([option for option in const_options if string in option])
        const_options = [x for x in const_options if x.startswith(string)]

        if(state == 0):
            # In case there is only one autocomplete option
            if(len(results) == 1):
                self.completeFound = True
                self.tabCount = 0
                return results[-1] + ' '
            
            # I need to add LCP mechanic for partial completion if availible
            is_LCP = True
            LCP_string = ''
            tester_string = string
            for char in const_options[0][len(tester_string):]:
                tester_string += char
                for element in const_options:
                    if element.startswith(tester_string):
                        continue
                    else:
                        is_LCP = False
                        break
                if(is_LCP):
                    LCP_string = tester_string
            if(len(LCP_string) > len(string)):
                self.completeFound = True
                self.tabCount = 0
                return LCP_string
                

            # for cases where command is miising only one letter but there are multiple autocomplete options 
            for i in range(len(results)):
                if(string == results[i][:-1] and len(results[i]) > 2):
                    self.completeFound = True
                    self.tabCount = 0
                    return results[i] + ' '

        # In case there is no decision of autocompletion, prepare for printing all autocomplete options

        if(len(const_options)-1>=state):
            print('\x07', end='', flush=True)
            self.doubleTabList = const_options
            return None

        return None

        
        

   #  --------------------------------------------------

    def main(self):

        self.readlineSet()

        # REPL
        while(True):
            self.userInput = ''


            self.userInput = input("$ ")
             
            if(self.userInput == ''):
                continue
            userInputSplit = formatting.formatInput(self.userInput)
            self.outRedirectFlag = False
            self.errRedirectFlag = False
            self.outputList = []
            self.errList = []
            if('1>' in userInputSplit  or '1>>' in userInputSplit):
                self.outRedirectFlag = True
            if('2>' in userInputSplit or '2>>' in userInputSplit):
                self.errRedirectFlag = True
            executeOutput = self.execute(userInputSplit)



if __name__ == '__main__':
    newShell = Shell()
    newShell.main()

