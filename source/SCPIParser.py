import re
import itertools

def argument_parser(argument):
    argument = argument.strip()
    if argument[0] in ['"', "'"] and argument[-1] in ['"', "'"] and argument[0] == argument[-1]:
        return argument[1:-1]
    if argument.upper().startswith('#H'):
        return int(argument[2:], 16)
    if argument.upper().startswith('#Q'):
        return int(argument[2:], 8)
    if argument.upper().startswith('#B'):
        return int(argument[2:], 2)
    if argument == 'ON':
        return True
    if argument == 'OFF':
        return False
    try:
        if '.' in argument or 'e' in argument or 'E' in argument:
            return float(argument)
        return int(argument)
    except ValueError:
        return argument
    
def name_parser(name):
    sections = re.split(r'(\[:[^\]]+\])', name)
    fixed = sections[0::2]
    optional = [s[1:-1] for s in sections[1::2]]
    
    choices = [(option, "") for option in optional]
    combinations = itertools.product(*choices)
    names = []
    for combination in combinations:
        name = fixed[0]
        for o, f in zip(combination, fixed[1:]):
            name += o + f
        name = name.replace(' ', '')
        if name[0] == ':':
            name = name[1:]
        names.append(name.split(':'))
    return names

def match(query, key):
    return query.upper() == key.upper() or query.upper() == ''.join([i for i in key if i.isupper() or i == '?'])

class Tree:
    """A tree structure to hold SCPI command names and their associated functions."""
    def __init__(self, name, value=None):
        """Initialize a tree node with a name and an optional functional value.
        
        Args:
            name (str): The name of the command or node.
            value (callable, optional): The function associated with this command. Defaults to None.
        
        Example:
            >>> tree = Tree('MEASURE', lambda x: x * 2)
        """
        self.name = name
        self.value = value
        self.children = []

    def select_child(self, name):
        """Select a matching child node based on the provided name."""
        for child in self.children:
            if match(name, child.name):
                return child
        return None
    
    def add(self, name, value):
        """Add a new command name, and function pair to the tree.
        
        Args:
            name (list): A list of command segments.
            value (callable): The function to associate with the command.
        
        Example:
            >>> tree.add(['MEASURE', 'VOLTAGE?'], lambda x: x * 2)
        """
        if len(name) == 0:
            self.value = value
            return
        child = self.select_child(name[0])
        if child is None:
            child = Tree(name[0])
            self.children.append(child)
        child.add(name[1:], value)
    
    def get(self, name):
        """Retrieve the function associated with the command name.
        
        Args:
            name (list): A list of command segments.
        
        Returns:
            callable: The function associated with the command, or None if not found.
        
        Example:
            >>> func = tree.get(['MEASURE', 'VOLTAGE?'])
            >>> if func:
            >>>     result = func(5)  # Assuming func is a callable
            >>>     print(result)
        """
        if len(name) == 0:
            return self.value
        child = self.select_child(name[0])
        if child is None:
            return None
        return child.get(name[1:])
    
class SCPIParser:
    """A parser for SCPI commands that allows registration and execution of commands.
    
    Attributes:
            commands (Tree): A tree structure to hold the command names and their associated functions.
    """
    def __init__(self, commands=dict()):
        """Initialize the SCPIParser with a dictionary of commands.
        
        Args:
            commands (dict): A dictionary where keys are command names and values are functions to execute.
        
        Example:
            >>> commands = {
            >>>    'MEASURE:VOLTAGE?': measure_voltage,
            >>>    'MEASURE:CURRENT?': lambda x: measure_current(x),
            >>> }
            >>> parser = SCPIParser(commands)
        """
        self.commands = Tree('')
        for name, value in commands.items():
            for n in name_parser(name):
                self.commands.add(n, value)
    
    def register(self, name):
        """Decorator to register a function as a SCPI command.
        
        Args:
            name (str): The command name to register the function under.
        
        Returns:
            function: The decorator function that registers the command.
        
        Example:
            >>> @parser.register('MEASURE:VOLTAGE?')
            >>> def measure_voltage():
            >>>     return 'Voltage measured'
        """
        def decorator(func):
            for n in name_parser(name):
                self.commands.add(n, func)
            return func
        return decorator
    
    def execute(self, string):
        """Execute a SCPI command string and return the results.
        
        Args:
            string (str): The SCPI command string to execute.
        
        Returns:
            str: The results of the executed commands, joined by commas.
        
        Example:
            >>> result = parser.execute('MEASURE:VOLTAGE?; :MEASURE:CURRENT?')
            >>> print(result)
        """
        commands = string.split(";")
        results = []
        context = ':'
        for command in commands:
            command = command.strip()
            if not command:
                continue
            arguments = []
            if ' ' in command:
                command, arg_string = command.split(' ', 1)
                args = re.compile(r'"(?:[^"]|"")*"|\'[^\']*\'|[^,]+').findall(arg_string)
                arguments = [argument_parser(arg) for arg in args]
            if command.startswith(':'):
                context = command
            else:
                context = context.rsplit(':', 1)[0] + ':' + command
            output = self.commands.get(context.split(':')[1:])(*arguments)
            if command.endswith('?'):
                results.append(str(output))
        if results:
            return ', '.join(results)
        return None