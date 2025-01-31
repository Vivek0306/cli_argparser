'''
TODO: 
    - Implement a verbose option that would allow detailed explanation of each argument if included
'''



from multiprocessing.sharedctypes import Value
from pydoc import describe
import sys


RED = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"
YELLOW = "\033[93m"

class Namespace:
    def __init__(self, **kwargs):
        '''Dynamic storage of arguments passed'''
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __repr__(self):
        '''Custom representation to print arguments like argparse.Namespace'''
        args = ", ".join(f"{key}={value}" for key, value in self.__dict__.items())
        return f"Namespace({args})"

class ArgumentParser:
    def __init__(self, description = 'Welcome!', strict = True):
        '''
        Argument Parser

        Initialize an empty dictionary to store the custom arguments passed.
        Once the arguments are parsed we store it to the parsed_args dictionary
        '''
        self.description = description
        self.arguments = {}
        self.parsed_args = {}
        self.strict = strict
        self.arguments['--help'] = {
            'required': False,
            'alias': '-h',            
            'help': 'Shows the help message and exits the program.',
            'action': 'store_true'
        }
        self.arguments['--verbose'] = {
            'required': False,
            'alias': '-v',            
            'help': 'Enhances output visibility of the program.',
            'action': 'store_true'
        }
    def _handle_error(self, message):
        '''
        Handle errors and show users error messages based on strict mode.

        :param message: Error message to display or raise.
        '''
        error_msg = f"{RED}[ERROR]: {message}{RESET}\nUse `--help` for more information."
        if self.strict:
            print(f"{YELLOW}[MESSAGE]: Showing traceback since 'Strict' mode is enabled. To disable, set `strict=False`.{RESET}", file=sys.stderr)
            raise ValueError(error_msg)
        else:
            print(error_msg, file=sys.stderr)
            sys.exit(2)

    def print_help(self, verbose = False):
        usage_text = f"usage: python {sys.argv[0]} " + " ".join(f"[{arg}]/[{self.arguments[arg]['alias']}]" if self.arguments[arg].get('alias') else f"[{arg}]"\
            for arg in self.arguments.keys())
            
        helper_text = f'''{self.description} 

{usage_text}

options:'''


        for arg, props in self.arguments.items():
            aliases = f"{arg}, {props['alias']}" if props['alias'] else arg
            helper_text += f"\n  {aliases:<20}    {props['help']}"

        if verbose:
            required_args = [arg for arg, props in self.arguments.items() if props['required']]
            optional_args = [arg for arg, props in self.arguments.items() if not props['required']]

            if required_args:
                helper_text += "\n\nRequired Arguments:"
                for arg in required_args:
                    props = self.arguments[arg]
                    aliases = f"{arg}, {props['alias']}" if props['alias'] else arg
                    helper_text += f"\n  {aliases:<20}    {props['help']}"

            if optional_args:
                helper_text += "\n\nOptional Arguments:"
                for arg in optional_args:
                    props = self.arguments[arg]
                    aliases = f"{arg}, {props['alias']}" if props['alias'] else arg
                    helper_text += f"\n  {aliases:<20}    {props['help']}"



        return helper_text




    def add_argument(self, name, alias = None, required = False, help = None, action = None):
        '''
        Add New Argument

        Each Argument would have 3 properties:
            - name => Name of the actual argument (e.g., '--arrange').
            - alias => Shortened single-hyphen form (e.g., '-a').
            - required => Whether it is required to supply the argument while running the code.
            - help => Help message describing the argument.
            - action => Special actions that needs to be done.

        :param name: Name of the argument (must start with '--').
        :param alias: Alias for the argument (must start with '-').
        :param required: Whether the argument is required.
        :param help: Help message for the argument.
        :param action: Special action for the argument (e.g., 'store_true').

        '''

        if not name.startswith("--"):
            self._handle_error("Arguments should start with '--' or '-'.")

        if alias and not alias.startswith("-"):
            self._handle_error("Aliases should start with '-'.")


        self.arguments[name] = {
            'required': required,
            'alias': alias,            
            'help': help,
            'action': action
        } 
    
    def parse_args(self):
        '''
        Used to parse the passed command-line arguments
        '''
        input_args = sys.argv[1:]
        input_dict = {}

        if '--help' in input_args or '-h' in input_args:
            if '--verbose' in input_args or '-v' in input_args:
                print(self.print_help(verbose=True))
            else:
                print(self.print_help())
            sys.exit(0)


        for i in range(len(input_args)):
            key = input_args[i]
            for long_form, properties in self.arguments.items():
                if key == long_form or key == properties['alias']:
                    if i + 1 < len(input_args) and not input_args[i+1].startswith('-'):
                        input_dict[long_form] = input_args[i+1]
                    else:
                        input_dict[long_form] = True
        
        if not input_dict and len(input_args) > 0:
            self._handle_error(f"Invalid options used.")
            sys.exit(1)
        
        if not input_dict:
            print(f"{self.description}{YELLOW}\n\nNo arguments provided. Use --help / -h to see available options.{RESET}")
            sys.exit(1)

        for arg, properties in self.arguments.items():
            if arg in input_dict:
                if properties['action'] == 'store_true':
                    self.parsed_args[arg.lstrip("--")] = True
                else:
                    self.parsed_args[arg.lstrip("--")] = input_dict[arg]
            elif properties['required']:
                self._handle_error(f"Missing required argument: {arg}")
            else:
                self.parsed_args[arg.lstrip("--")] = False if properties["action"] == "store_true" else None    

        return Namespace(**self.parsed_args)