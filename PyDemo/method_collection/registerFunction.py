import ast

import allure
import chardet
from comm.script.writeLogs import logger
from config import *
from PyDemo.method_collection import request_in_a_function
from comm.unit.GlobalVariable import GlobalData
from comm.utils.SoapParser import xml_to_dict, SoapParser
from comm.utils.randomly import *


def collect_functions(directory):
    functions = {}
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py") and file != "registerFunction.py":
                filepath = os.path.join(root, file).replace("\\", "/")
                with open(filepath, 'rb') as f:
                    content = f.read()
                encoding = chardet.detect(content)['encoding']
                with open(filepath, encoding=encoding) as f:
                    tree = ast.parse(f.read())
                for node in tree.body:
                    if isinstance(node, ast.FunctionDef):
                        functions[node.name] = node
    return functions


def call_function(function_name, *args, **kwargs):
    allure.attach(name=f"function name：{function_name}", body=str(args)+" "+str(kwargs))
    functions = collect_functions('./PyDemo/method_collection')
    if function_name not in functions:
        raise ValueError(f"Function {function_name} not found")
    node = functions[function_name]
    code = compile(ast.Module(body=[node]), "<ast>", "exec")
    globals_dict = globals()
    locals_dict = locals()['functions']
    exec(code, globals_dict, locals_dict)
    function = locals_dict[function_name]
    function_args = list(node.args.args)
    function_defaults = [None] * (len(function_args) - len(node.args.defaults))
    function_defaults += node.args.defaults
    function_dict = dict(zip(function_args, function_defaults))
    function.__defaults__ = tuple(function_dict.values())
    function(*args, **kwargs)
