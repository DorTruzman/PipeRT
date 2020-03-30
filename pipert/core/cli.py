import os

import yaml
import zerorpc
from yaml.scanner import ScannerError
import sys
from subprocess import call

EXIT_METHOD_TEXT = 'exit'
SHOW_METHODS_TEXT = 'show_methods'
LOAD_CONFIG_FILE_TEXT = "load_config_file"
EXPORT_CONFIG_FILE_TEXT = "export_config_file"
CLEAR_CONSOLE_TEXT = 'clear'

clear_console = lambda: call('clear' if os.name == 'posix' else 'cls')


def execute_method(method_name, connection):
    parameters_values = {}
    parameters = connection.get_method_parameters(method_name)
    for parameter_name in parameters:
        if parameter_name == 'self':
            continue
        elif "kwargs" in parameter_name:
            user_input = input("Enter key - value for " + parameter_name + ". To stop enter stop: ")
            while user_input != "stop":
                try:
                    key, value = user_input.split("-")
                    parameters_values[key.strip()] = value.strip()
                except ValueError:
                    print("Can't parse", user_input, "to key - value format")
                user_input = input("Enter key - value for " + parameter_name + ". To stop enter stop: ")
        else:
            parameters_values[parameter_name] = input("Enter value for " + parameter_name + ": ")
    return connection.execute_method(method_name, parameters_values)


connection = zerorpc.Client()
# endpoint = input("Enter a zerorpc endpoint to connect to: ")
endpoint = "tcp://0.0.0.0:4001"
connection.connect(endpoint)
try:
    print("Connecting to", endpoint + "...")
    if connection.check_connection():
        print("Connected successfully")
except zerorpc.LostRemote:
    sys.exit("Unable to connect to " + endpoint)

# TODO - refactor this to be dynamic
methods = connection.get_methods()
methods.insert(0, EXIT_METHOD_TEXT)
methods.insert(1, SHOW_METHODS_TEXT)
methods.insert(2, LOAD_CONFIG_FILE_TEXT)
methods.insert(3, EXPORT_CONFIG_FILE_TEXT)
methods.insert(4, CLEAR_CONSOLE_TEXT)
print(methods)
user_input = input("Enter method to execute: ")
while user_input != EXIT_METHOD_TEXT:
    if user_input == SHOW_METHODS_TEXT:
        print(methods)
    elif user_input == LOAD_CONFIG_FILE_TEXT:
        file_path = input("Enter the config file path: ")
        try:
            with open(file_path) as config_file:
                # /home/internet/Desktop/components.yaml
                components = yaml.load(config_file, Loader=yaml.FullLoader)
            print(connection.execute_method("setup_components", {"components": components}))
        except FileNotFoundError as error:
            print(error.args[1], "'{}'".format(file_path))
        except IsADirectoryError as error:
            print("'{}' is a directory not a file".format(file_path))
        except ScannerError:
            print("Expecting yaml file, can't parse the file '{}'".format(file_path))
    elif user_input == EXPORT_CONFIG_FILE_TEXT:
        with open("config_file.yaml", 'w') as config_file:
            documents = yaml.dump(connection.
                                  execute_method("get_pipeline_creation", {}),
                                  config_file)
            print(documents)
    elif user_input == CLEAR_CONSOLE_TEXT:
        clear_console()
    elif user_input in methods:
        print(execute_method(user_input, connection))
    user_input = input("Enter method to execute : ")
