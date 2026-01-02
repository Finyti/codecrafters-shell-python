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
This lead to next objective:
2. Add per-comand output handling.
Input -> processing -> Commands -> execute = output -> command -> memory object
Command object has a flag inputRedirection to indicate whether or not it
should be 
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


class Shell:
    
    def __init__(self):
        self.workingDirectory = os.path.abspath("")
        self.userInput = ''

        self.commandDict = {'exit': self.exitFunc,
            'echo': self.echo,
            'type': self.typeOfArgument,
            'execute': self.execute,
            'pwd': navigation.NavigationModule.pwd,
            'cd': navigation.NavigationModule.cd}
        
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

        
   #  --------------------------------------------------
#    SIMPLE BUILTINS

    def exitFunc(self, exitStatus):
        if(len(exitStatus) == 0 or int(exitStatus[0]) not in (0, 1)):
            exit(0)
        exit(int(exitStatus[0])) 

    def echo(self, text):
        self.addStdFeedback(' '.join(text), "")
        return

    def typeOfArgument(self, commands):
        """
        Accepts two variables. \n
        'command' - command to check \n
        'commandDict' - Dictionary with all builtin commands \n \n

        If command is an executable, returns a touple with [0] being 'command' name and [1] being valid path \n
        or None in any other case
        """
        # Check if command is a builtin functions
        for command in commands:
            if(helpers.inCommandDict(command, self.commandDict)):
                # print(f'{command} is a shell builtin')
                self.addStdFeedback(f'{command} is a shell builtin', "")
                continue
            
            # If not builtin, check if command is a an executable accesible in any of the locations in PATH
            validExec = helpers.getExec(command)
            if(validExec != None):
                # print(f'{command} is {validExec[1]}/{command}')
                self.addStdFeedback(f'{command} is {validExec[1]}/{command}', "")
                continue
            
            self.addStdFeedback("", f'{command}: not found')



    #  --------------------------------------------------
#    DEALS WITH EXECUTABLES

    def executePrep(self, fullCommand):

        untrimedExecutable = fullCommand[0]
        args = fullCommand[1:]
        path = ''
        command = ''
        if(untrimedExecutable[0] == '.'):
            untrimedExecutable = untrimedExecutable[1:]

        # if givven command preceeded by full path
        if(os.path.sep in untrimedExecutable):
            path = untrimedExecutable.split(os.path.sep)[:-1]
            path = os.path.sep.join(path)
            command = untrimedExecutable.split(os.path.sep)[-1]
        # if givven only the command name
        else:
            command = untrimedExecutable
            validExec = helpers.getExec(command)
            if(validExec != None):
                path = validExec[1]
        # First format the string (quotes compatability) for passing the command and the arguments, then execute the whole command
        if((command in self.commandDict or command in self.commandModificatorsDict)):

            argsString = args
            return command,argsString
        if(path != '' and helpers.isExec(command, path)):
            argsString = args
            return command,argsString
        else:
            sys.stdout.write(f'{command}: command not found' + '\n')
            return ""

    def execute(self, fullCommand):
        commandList = helpers.separateCommands(fullCommand, self.commandDict, self.commandModificatorsDict)

        for command in commandList:
            executableAndArgs = self.executePrep(command)
            if(executableAndArgs == ''):
                continue
            
            # Problem, right now I handle outputs globaly. I do not support per-command output handling
            # because multiple comands in one line are not supported. Because of that I handle redirections 
            # as disablers for output. The solutions is pretty.. brute forcy and I want to add multi-comand support
            # with ';'. Output must be an array of Memory type objects (to not just store, but support flags)

            if(self.pipeActive):
                output = subprocess.run(command, input=self.outputList[-1], capture_output = True)

                stdout = output.stdout
                stderr = output.stderr
                self.addStdFeedback(stdout, stderr)
                self.pipeActive = False
                continue

            if(executableAndArgs[0] == 'exit'):
                self.commandDict[executableAndArgs[0]](executableAndArgs[1])

            elif(executableAndArgs[0] == 'echo'):
                self.commandDict[executableAndArgs[0]](executableAndArgs[1])

            elif(executableAndArgs[0] == 'type'):
                self.commandDict[executableAndArgs[0]](executableAndArgs[1])

            elif(executableAndArgs[0] == 'pwd'):
                self.commandDict[executableAndArgs[0]](self)

            elif(executableAndArgs[0] == 'cd'):
                if(len(executableAndArgs) > 1):
                    if(len(executableAndArgs[1]) > 0):
                        self.commandDict[executableAndArgs[0]](executableAndArgs[1][0], self)

            elif(executableAndArgs[0] == '1>'):
                redirection.redirect(self.outputList[0].decode("utf-8"), executableAndArgs[1])
            elif(executableAndArgs[0] == '1>>'):
                redirection.append(self.outputList[0].decode("utf-8"), executableAndArgs[1])
            elif(executableAndArgs[0] == '2>'):
                redirection.redirect(self.errList[0].decode("utf-8"), executableAndArgs[1])
            elif(executableAndArgs[0] == '2>>'):
                redirection.append(self.errList[0].decode("utf-8"), executableAndArgs[1])
            


                        
            elif(executableAndArgs[0] == '|'):
                self.pipeActive = True

            else:
                output = subprocess.run(command, capture_output = True)

                stdout = output.stdout
                stderr = output.stderr
                self.addStdFeedback(stdout, stderr)

        if(not self.outRedirectFlag):
            self.printStdOut()


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

