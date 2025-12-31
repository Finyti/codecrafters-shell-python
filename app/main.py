import sys
import os
import subprocess

import readline

import app.navigation as navigation
import app.formatting as formatting
import app.helpers as helpers
import app.redirection as redirection


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
                                        '2>>': redirection.append}

        self.outputList = []
        self.errList = []
        self.outRedirectFlag = False
        self.errRedirectFlag = False

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
                redirection.redirect(self.outputList[0], executableAndArgs[1])
            elif(executableAndArgs[0] == '1>>'):
                redirection.append(self.outputList[0], executableAndArgs[1])
            elif(executableAndArgs[0] == '2>'):
                redirection.redirect(self.errList[0], executableAndArgs[1])
            elif(executableAndArgs[0] == '2>>'):
                redirection.append(self.errList[0], executableAndArgs[1])
                


            else:
                output = subprocess.run(command, capture_output = True)

                stdout = output.stdout.decode("utf-8")
                stderr = output.stderr.decode("utf-8")
                self.addStdFeedback(stdout, stderr)

        if(not self.outRedirectFlag):
            self.printStdOut()


   #  --------------------------------------------------
#    DEALS WITH OUTPUTS AND ERROR_OUTPUTS

    def addStdFeedback(self, output, err):
        # if(output!=''):
        #     print(output)
        if(err!='' and not self.errRedirectFlag):
            if(err[-1] != '\n'):
                sys.stdout.write(err + '\n')
            else:
                sys.stdout.write(err)
            # (Resets the loop instead of returning to wherever)
        self.outputList.append(output)
        self.errList.append(err)

    def printStdOut(self):
        if(len(self.outputList) == 0):
            return
        for index, output in enumerate(self.outputList):
            if(len(output) == 0):
                return
            if(index == len(self.outputList)-1 and output[-1] == '\n'):
                sys.stdout.write(output[0:-1])
            elif(index < len(self.outputList)-1 and output[-1] != '\n'):
                sys.stdout.write(output + '\n')
            else:
                sys.stdout.write(output)
        sys.stdout.write('\n')



   #  --------------------------------------------------
#   AUTOCOMPLETION

    def readlineSet(self):
        readline.parse_and_bind('set editing-mode vi') 
        readline.set_completer(self.complete)
        delims = readline.get_completer_delims()
        delims = delims.replace('-', '')
        readline.set_completer_delims(delims)
        # readline.parse_and_bind('bind ^I rl_complete')
        # Detect libedit vs GNU readline
        doc = readline.__doc__ or ""
        if "libedit" in doc:
            # libedit-style binding
            readline.parse_and_bind("bind ^I rl_complete")
        else:
            # GNU readline-style binding
            readline.parse_and_bind("tab: complete")


        # readline.parse_and_bind("set show-all-if-ambiguous off")
        # readline.set_completion_display_matches_hook(self.display_matches)

    def complete(self, string, state):
        
        if(string == ''):
            return None
        
        if(state == 0):
            self.tabCount +=1
            self.completeFound = False

        if(self.tabCount == 2):
            print('\n' + "  ".join(self.doubleTabList))
            self.doubleTabList = []
            self.tabCount = 0
            buffer = readline.get_line_buffer()
            print("$ " + buffer, end="", flush=True)
            return None
        

        if(self.completeFound):
            print('\x07', end='', flush=True)
            return None

        const_options = list(self.commandDict.keys()) + helpers.getAllExec(os.environ['PATH'].split(os.pathsep))
        const_options = list(dict.fromkeys(const_options))
        results = []
        for key in const_options:
            if string in key:
                results.append(key)


        const_options = sorted([option for option in const_options if string in option])

        if(state == 0):
            if(len(results) == 1):
                self.completeFound = True
                return results[-1] + ' '
            for i in range(len(results)):
                if(string == results[i][:-1] and len(results[i]) > 2):
                    self.completeFound = True
                    return results[i] + ' '
                
        const_options = [x for x in const_options if x.startswith(string)]
        if(len(const_options)-1>=state):
            print('\x07', end='', flush=True)
            self.doubleTabList = const_options
            return None

        return None

        
    # def display_matches(self, substitution, matches, longest):
    #     line = "  ".join(matches)
    #     sys.stdout.write("\n" + line + "\n")

    #     # Re-print prompt and current text (readline buffer)
    #     buffer = readline.get_line_buffer()
    #     sys.stdout.write("$ " + buffer)
    #     sys.stdout.flush()
        

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

