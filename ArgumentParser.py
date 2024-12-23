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

    def add_argument(self, name, alias = None, required = False, help = None, action = None):
        '''
        Add New Argument

        Each Argument would have 3 properties:
            - name => Name of the actual argument (e.g., '--arrange').
            - alias => Shortened single-hyphen form (e.g., '-a').
            - required => Whether it is required to supply the argument while running the code.
            - help => Help message describing the argument.
            - action => Special actions that needs to be done.

        '''

        if not name.startswith("--"):
            raise ValueError("Arguments should start with '--' or '-'.")

        if alias and not alias.startswith("-"):
            raise ValueError("Aliases should start with '-'.")

        self.arguments[name] = {
            'required': required,
            'alias': alias,            
            'help': help,
            'action': action
        } 
    
    def print_help(self):
        usage_text  = f"usage: {sys.argv[0]} [-h] " + " ".join(map(lambda x: f'[{x}]', list(self.arguments.keys())))
        header_txt = f'''{usage_text} 

{self.description}

options:'''
        for arg, props in self.arguments.items():
            aliases = f"{arg}, {props['alias']}" if props['alias'] else arg
            header_txt += f"\n  {aliases:<20}    {props['help']}"
        return header_txt

    def parse_args(self):
        '''
        Used to parse the passed command-line arguments
        '''
        input_args = sys.argv[1:]
        input_dict = {}

        if '--help' in input_args or '-h' in input_args:
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

        if not input_dict:
            print("No arguments provided. Use --help to see available options.")
            sys.exit(1)  

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