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
    return query.upper() == key.upper() or query.upper() == ''.join([i for i in key if i.isupper()])

class Tree:
    def __init__(self, name, value=None):
        self.name = name
        self.value = value
        self.children = []

    def select_child(self, name):
        for child in self.children:
            if match(name, child.name):
                return child
        return None
    
    def add(self, name, value):
        if len(name) == 0:
            self.value = value
            return
        child = self.select_child(name[0])
        if child is None:
            child = Tree(name[0])
            self.children.append(child)
        child.add(name[1:], value)
    
    def get(self, name):
        if len(name) == 0:
            return self.value
        child = self.select_child(name[0])
        if child is None:
            return None
        return child.get(name[1:])
    
class SCPIParser:
    def __init__(self, commands=dict()):
        self.commands = Tree('')
        for name, value in commands.items():
            for n in name_parser(name):
                self.commands.add(n, value)
    
    def register(self, name):
        def decorator(func):
            for n in name_parser(name):
                self.commands.add(n, func)
            return func
        return decorator
    
    def execute(self, string):
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
        return ', '.join(results)