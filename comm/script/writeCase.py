# -*- coding:utf-8 -*-
# @Time    : 2021/07/10
# @Author  : Xuanyu Liu
# @File    : writeCase.py
# ************************
import os
from config import ROOT_DIR, TEST_DIR
from comm.script.writeCaseYml import write_case_yaml, read_yaml_data
temp_file = ROOT_DIR+'config/test_template.py'


def write_case(case_path, auto_yaml=True):
    """
    :param case_path: 用例路径，当auto_yaml为True时，需要传入data目录，否则传入扫描目录
    :param auto_yaml: 是否自动生成yaml文件
    :return:
    """
    # 判断是否自动生成yaml用例
    if auto_yaml:
        yaml_list = write_case_yaml(case_path)
    else:
        yaml_list = list()
        file_list = os.listdir(case_path)    # 读取测试用例路径下所有测试目录 (以test开头 .yaml结尾)
        for file in file_list:
            if os.path.isfile(case_path+'/' + file):
                if 'test' in file and '.yaml' in file:
                    yaml_path = case_path+'/'+file
                    yaml_list.append(yaml_path)
            else:
                filelist = os.listdir(case_path+'/' + file)
                for fileyaml in filelist:
                    yamlpath = case_path + '/' + file + '/' + fileyaml
                    if os.path.isfile(yamlpath) and 'test' in fileyaml and '.yaml' in fileyaml:
                        yaml_list.append(yamlpath)

                # 遍历测试用例列表
    for yaml_file in yaml_list:
        test_data = read_yaml_data(yaml_file)
        test_script = yaml_file.replace('page', 'testcase').replace('.yaml', '.py')
        # case_name = os.path.basename(test_script).replace('.py', '')
        case_path = os.path.dirname(test_script)
        # 判断文件路径是否存在
        if not os.path.exists(case_path):
            os.makedirs(case_path)
        # 判断测试用例脚本是否已经生成
        if os.path.exists(test_script):
            continue
        # 替换模板内容
        file_data = ''
        with open(temp_file, "r", encoding="utf-8") as f:
            for line in f:
                if 'TestTemplate' in line:
                    # title = test_data['test_info']['title']
                    title = test_data['test_info']['feature']
                    line = line.replace('Template', title.title())
                if 'test_template' in line:
                    if '@allure.story' in line:
                        # describe = test_data['test_case'][0]['describe']
                        describe = test_data['test_info']['story']
                        line = line.replace('test_template', describe)
                    else:
                        summary = test_data['test_case'][0]['summary']
                        line = line.replace('template', summary)
                file_data += line

        # 写入新脚本
        with open(test_script, "w", encoding="utf-8") as f:
            f.write(file_data)


def alter(file, mode=1):
    """
    将替换的字符串写到一个新的文件中，然后将原文件删除，新文件改为原来文件的名字
    :param mode: 1- 2-
    :param file: 接口命名
    :return: None
    """
    old_str = "# @pytest.mark.skip"
    new_str = "@pytest.mark.skip"
    if mode != 1:
        old_str = "@pytest.mark.skip"
        new_str = "# @pytest.mark.skip"
    file = search_file(file)
    with open(file, "r", encoding="utf-8") as f1, open("%s.bak" % file, "w", encoding="utf-8") as f2:
        for line in f1:
            if old_str in line:
                line = line.replace(old_str, new_str)
            f2.write(line)
    os.remove(file)
    os.rename("%s.bak" % file, file)


def search_file(file_name, pathsep=os.pathsep, search_path=TEST_DIR):
    """
    用例文件搜索
    :param file_name: 接口命名
    :param search_path:
    :param pathsep:
    :return:
    """
    for path in search_path.split(pathsep):
        filelist = os.listdir(search_path)
        file_name = "test_" + file_name + ".py"
        candidate = os.path.join(path, file_name)
        if os.path.isfile(candidate):
            return os.path.abspath(candidate)
        else:
            for _dir in filelist:
                candidate = os.path.join(search_path, _dir, file_name)
                if os.path.isfile(candidate):
                    return os.path.abspath(candidate).replace("\\", "/")
    return None


if __name__ == '__main__':
    # real_path = os.path.dirname(os.path.realpath(__file__)).replace('\\', '/')
    # write_case(real_path + '/data', auto_yaml=True)
    # write_case(r"D:\pythonProject\ApiTesting\PyDemo\page", auto_yaml=False)
    # search_path = r'D:\pythonProject\ApiTesting-XM\PyDemo\testcase'
    alter("v2CategoryDetail")