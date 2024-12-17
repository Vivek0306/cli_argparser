import sys

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
    def __init__(self, description = None):
        '''
        Argument Parser

        Initialize an empty dictionary to store the custom arguments passed.
        Once the arguments are parsed we store it to the parsed_args dictionary
        '''
        self.description = description
        self.arguments = {}
        self.parsed_args = {}

    def add_argument(self, name, required = False, help = None, action = None):
        '''
        Add New Argument

        Each Argument would have 3 properties:
            - name => Name of the actual argument.
            - required => Whether it is required to supply the argument while running the code.
            - help => Help message describing the argument.
            - action => Special actions that needs to be done.

        '''

        if not name.startswith("--"):
            raise ValueError("Arguments should start with '--'.")

        self.arguments[name] = {
            'required': required,
            'help': help,
            'action': action
        } 
    
    def print_help(self):
        header_txt = f'''usage: {sys.argv[0]}

File Organizer CLI Tool - Arrange files into directories based on file types or undo the arrangement.

options:'''
        for arg, props in self.arguments.items():
            header_txt += f"\n  {arg:<15}    {props['help']}"
        return header_txt

    def parse_args(self):
        '''
        Used to parse the passed command-line arguments
        '''
        input_args = sys.argv[1:]
        input_dict = {}

        for i in range(len(input_args)):
            if input_args[i].startswith('--'):
                key = input_args[i]
                if i + 1 < len(input_args) and not input_args[i+1].startswith('--'):
                    input_dict[key] = input_args[i+1]
                else:
                    input_dict[key] = True

        if not input_dict:
            print("No arguments provided. Use --help to see available options.")

        for arg, properties in self.arguments.items():
            if arg in input_dict:
                if properties['action'] == 'store_true':
                    self.parsed_args[arg.lstrip("--")] = True
                else:
                    self.parsed_args[arg.lstrip("--")] = input_dict[arg]
            elif properties['required']:
                raise ValueError(f"[ERROR]: Missing required argument: {arg}")
            else:
                self.parsed_args[arg.lstrip("--")] = False if properties["action"] == "store_true" else None    

        return Namespace(**self.parsed_args)