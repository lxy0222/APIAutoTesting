from config import ROOT_DIR
import os
from comm.script.writeCaseYml import write_case_yaml, read_yaml_data
temp_file = ROOT_DIR+'config/test_template.py'
temp_function_file = ROOT_DIR+'config/FunctionTemplate.py'


def write_case(case_path, auto_yaml=True, target_path=None):
    """
    :param case_path: use case path. When auto_yaml is True, the data directory is passed in, otherwise the scan directory is passed in
    :param auto_yaml: Specifies whether to automatically generate yaml files
    :param target_path: Target path for generating script storage
    :return: None
    """
    if target_path is None:
        target_path = case_path.replace('page', 'testcase')

    if auto_yaml:
        yaml_list = write_case_yaml(case_path)
    else:
        yaml_list = list()
        for root, dirs, files in os.walk(case_path):
            for file in files:
                if 'test' in file and '.yaml' in file:
                    yaml_path = os.path.join(root, file)
                    yaml_list.append(yaml_path)

    for yaml_file in yaml_list:
        test_data = read_yaml_data(yaml_file)

        relative_path = os.path.relpath(yaml_file, case_path)
        test_script = os.path.join(target_path, relative_path.replace('.yaml', '.py'))

        case_dir = os.path.dirname(test_script)
        method_script = os.path.dirname(test_script).replace('testcase', 'method_collection')
        if not os.path.exists(case_dir):
            os.makedirs(case_dir)
        if not os.path.exists(method_script):
            os.makedirs(method_script)
            with open(temp_function_file, "r", encoding="utf-8") as f:
                file_content = ""
                for line in f:
                    file_content += line
            with open(os.path.join(method_script, "Function.py"), "w", encoding="utf-8") as f:
                f.write(file_content)

        if os.path.exists(test_script):
            continue

        file_data = ''
        with open(temp_file, "r", encoding="utf-8") as f:
            for line in f:
                if 'TestTemplate' in line:
                    title = test_data['test_info']['feature']
                    line = line.replace('Template', title.title())
                if 'test_template' in line:
                    if '@allure.story' in line:
                        describe = test_data['test_info']['story']
                        line = line.replace('test_template', describe)
                    else:
                        summary = test_data['test_info']['story']
                        line = line.replace('template', summary)
                file_data += line

        with open(test_script, "w", encoding="utf-8") as f:
            f.write(file_data)
