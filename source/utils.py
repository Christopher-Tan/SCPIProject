import yaml
import os

path_separator = "#"
config_separator = "|"
SCPI_argument_separator = ","
SCPI_command_separator = ";"


REL_FUNCTION_1 = 4
REL_FUNCTION_2 = 17
REL_FUNCTION_3 = 25
REL_FUNCTION_4 = 27
REL_FUNCTION_5 = 22

HEARTBEAT = 18

def read_config():
    with open(os.path.join(os.path.dirname(__file__), "config.yaml"), 'r') as file:
        return yaml.safe_load(file)
    
def write_config(config):
    with open(os.path.join(os.path.dirname(__file__), "config.yaml"), 'w') as file:
        yaml.dump(config, file, default_flow_style=False)

def stringify(dic, prefix=""):
    """Convert a dictionary to a string representation."""
    s = ""
    for key, value in dic.items():
        name = f'{prefix}{path_separator}{key}' if prefix else key
        if isinstance(value, dict):
            s += f'{config_separator if s else ""}{stringify(value, name)}'
        else:
            if isinstance(value, str):
                value = f"'{value}'"
            s += f'{config_separator if s else ""}{name}{path_separator}{str(value)}'
    return s

def apply(dic, string):
    if not isinstance(string, str):
        return #Almost certainly a timing error
    if string.strip():
        for item in string.split(config_separator):
            k, v = item.rsplit(path_separator, 1)
            temp = dic
            keys = k.split(path_separator)
            
            for key in keys[:-1]:
                if key not in temp or not isinstance(temp[key], dict):
                    temp[key] = {}
                temp = temp[key]
            import ast
            temp[keys[-1]] = ast.literal_eval(v)

def shared_configs(config):
    m = stringify(config['measurement_devices'], prefix="measurement_devices")
    p = stringify(config['properties'], prefix="properties")
    return f"{m}{config_separator}{p}" if m and p else m+p