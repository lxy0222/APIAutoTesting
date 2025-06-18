# -*- coding:utf-8 -*-
# @File    : initialize.py
# **************************
import ast
import json
from comm.script.writeLogs import logger
import os
import re
import time
from json import JSONDecodeError
from config import PAGE_DIR, PROJECT_NAME, API_CONFIG
from comm.unit import apiSend, readRelevance, replaceRelevance
from comm.utils import readYaml


def read_json(summary, json_obj, case_path):
    """
    校验内容读取
    :param summary: 用例名称
    :param json_obj: json文件或数据对象
    :param case_path: case路径
    :return:
    """
    if isinstance(json_obj, dict) or isinstance(json_obj, list):
        return json_obj
    elif json_obj is None:
        return {}
    else:
        try:
            # 读取json文件指定用例数据
            with open(case_path+'/'+json_obj, "r", encoding="utf-8") as js:
                data_list = json.load(js)
                for data in data_list:
                    if data['summary'] == summary:
                        return data['body']
        except FileNotFoundError:
            raise Exception("用例关联文件不存在\n文件路径： %s" % json_obj)
        except JSONDecodeError as e:
            raise Exception(f"用例关联的文件有误\n文件路径： {json_obj},错误信息：{e}")


def call_function(**kwargs):
    """用于处理setup method的函数调用
    :param kwargs: setup_method 参数值
    :return:
    """
    from PyDemo.method_collection import func_dict
    if isinstance(kwargs, dict):
        for func_name, func_args in kwargs.items():
            func = func_dict.get(func_name)  # func_dict为函数字典映射
            if func:
                func(**func_args)
            else:
                print(f"Function '{func_name}' not found!")
    else:
        print("No support this object!")


def init_premise(test_info, case_data, case_path):
    """用例前提条件执行，提取关键值
    :param test_info: 测试信息
    :param case_data: 用例数据
    :param case_path: 用例路径
    :return:
    """
    # 获取项目公共关联值
    aconfig = readYaml.read_yaml_data(API_CONFIG)   # 项目基础信息
    # pconfig = readYaml.read_yaml_data(PARAM_CONFIG)   # 调用函数的参数信息
    # __relevance = {**aconfig[PROJECT_NAME], **pconfig}   # 将两个参数池合并
    __relevance = aconfig
    # 处理测试信息
    test_info = replaceRelevance.replace(test_info, __relevance)
    test_info = find_func(test_info)
    logger.debug("测试信息处理结果：{}".format(test_info))
    # 判断是否存在前置接口
    conf_path = case_data.get("premise", test_info.get("premise", False))
    if conf_path:
        conf_list = conf_path.split(" ")
        pre_case_path = conf_list[0]
        if pre_case_path:
            # 获取前置接口用例
            logger.info("获取前置接口测试用例：{}".format(pre_case_path))
            pre_case_path = PAGE_DIR + pre_case_path
            pre_case_row = int(conf_list[2])
            pre_case_dict = readYaml.read_yaml_data(pre_case_path)
            if conf_list[1] == "_":
                pre_test_info = pre_case_dict['test_info']
                pre_case_data = pre_case_dict['test_case'][pre_case_row]
            else:
                pre_case_api = conf_list[1]
                pre_test_info = pre_case_dict[pre_case_api]['test_info']
                pre_case_data = pre_case_dict[pre_case_api]['test_case'][pre_case_row]
            # 判断前置接口是否也存在前置接口
            if pre_case_data["premise"]:
                pre_case_path = os.path.dirname(pre_case_path)
                init_premise(pre_test_info, pre_case_data, pre_case_path)
            # 判断是否需要调用其他方法
            if pre_case_data["setup_function"]:
                pre_case_data["setup_function"] = replaceRelevance.replace(pre_case_data["setup_function"], __relevance)
                call_function(**pre_case_data["setup_function"])
            for i in range(3):
                # 处理前置接口测试信息
                pre_test_info = replaceRelevance.replace(pre_test_info, __relevance)
                pre_test_info = find_func(pre_test_info)
                logger.debug("测试信息处理结果：{}".format(pre_test_info))
                # 处理前置接口入参：获取入参-替换关联值-发送请求
                # 读取请求体
                if pre_case_path.endswith(".yaml"):
                    pre_case_path = os.path.dirname(pre_case_path)
                pre_parameter = read_json(pre_case_data['summary'], pre_case_data['parameter'], pre_case_path)
                # 替换apiConfig和PARAM_CONFIG参数关联池
                pre_parameter = replaceRelevance.replace(pre_parameter, __relevance)
                # 查找需要进行接口调用的参数
                pre_parameter = find_func(pre_parameter)
                # 替换requestConfig参数关联池  （要在替换为func_xxx进行调用后才能进行这个数据池的替换）
                __relevanceR = readYaml.read_yaml_data(REQUEST_CONFIG)
                pre_parameter = replaceRelevance.replace(pre_parameter, __relevanceR)
                # 赋值处理后的请求体
                pre_case_data['parameter'] = pre_parameter
                logger.debug("请求参数处理结果：{}".format(pre_parameter))
                logger.info("执行前置接口测试用例：{}".format(pre_test_info))
                # 请求
                code, data = apiSend.send_request(pre_test_info, pre_case_data)
                # 检查接口是否调用成功
                if data:
                    # 处理当前接口入参：获取入参-获取关联值-替换关联值
                    parameter = read_json(case_data['summary'], case_data['parameter'], case_path)
                    # 对请求参数全部解析
                    toData = dict(data, **pre_parameter)  # 合并前置接口请求参数和响应参数 出现相同key 以返回数据为先
                    pre_parameter_all = To.get_target_value(toData)  # 解析所有返回结果
                    __relevanceMer = dict(__relevance, **pre_parameter_all)
                    # 判断是否需要调用其他方法
                    if case_data["setup_function"]:
                        case_data["setup_function"] = replaceRelevance.replace(case_data["setup_function"],
                                                                                   __relevanceMer)
                        call_function(**case_data["setup_function"])
                    parameter = replaceRelevance.replace(parameter, __relevanceMer)
                    parameter = find_func(parameter)
                    # 替换requestConfig参数关联池
                    __relevanceR = readYaml.read_yaml_data(REQUEST_CONFIG)
                    parameter = replaceRelevance.replace(parameter, __relevanceR)
                    case_data['parameter'] = parameter
                    ###  再次处理auth
                    if case_data['auth']:
                        case_data['auth'] = replaceRelevance.replace(case_data['auth'], __relevanceR)
                    logger.debug("请求参数处理结果：{}".format(parameter))

                    # 获取当前接口期望结果：获取期望结果-获取关联值-替换关联值
                    expected_rs = read_json(case_data['summary'], case_data['check_body']['expected_result'], case_path)
                    __relevanceMer = readRelevance.get_relevance(parameter, expected_rs, __relevanceMer)
                    expected_rs = replaceRelevance.replace(expected_rs, __relevanceMer)
                    case_data['check_body']['expected_result'] = expected_rs
                    logger.debug("期望返回处理结果：{}".format(case_data))
                    break
                else:
                    time.sleep(1)
                    logger.error("前置接口请求失败！等待1秒后重试！")
            else:
                logger.info("前置接口请求失败！尝试三次失败！")
                raise Exception("获取前置接口关联数据失败！")
    else:
        # 处理当前接口入参：获取入参-获取关联值-替换关联值
        if 'parameter_pre' in case_data.keys():
            parameter_pre = replaceRelevance.replace(case_data['parameter_pre'], __relevance)
            # __relevance = dict(parameter_pre, **__relevance)
            __relevance["parameter_pre"] = parameter_pre
        # 判断是否需要调用其他方法
        if case_data["setup_function"]:
            case_data["setup_function"] = replaceRelevance.replace(case_data["setup_function"], __relevance)
            call_function(**case_data["setup_function"])
        parameter = read_json(case_data['summary'], case_data['parameter'], case_path)   # 返回的请求体
        parameter = replaceRelevance.replace(parameter, __relevance)   # 返回替换后的请求体
        parameter = find_func(parameter)
        # 替换requestConfig参数关联池
        __relevanceR = readYaml.read_yaml_data(REQUEST_CONFIG)
        parameter = replaceRelevance.replace(parameter, __relevanceR)
        case_data['parameter'] = parameter
        logger.debug("请求参数处理结果：{}".format(parameter))

        # 获取当前接口期望结果：获取期望结果-获取关联值-替换关联值
        expected_rs = read_json(case_data['summary'], case_data['check_body']['expected_result'], case_path)
        __relevance = readRelevance.get_relevance(parameter, expected_rs, __relevance)
        expected_rs = replaceRelevance.replace(expected_rs, __relevance)
        case_data['check_body']['expected_result'] = expected_rs
        logger.debug("期望返回处理结果：{}".format(case_data))
    return test_info, case_data


def find_func(input_json):
    """
    查找函数调用
    """
    pattern_all = re.compile(r'func_\w{0,}{\S{0,}\}')    # func_\w{0,}{\S{0,}\}   不能匹配空格
    pattern = re.compile(r'func_\w{0,}')
    if isinstance(input_json, str) and "sql" in input_json:
        input_json = func_DoSql(**eval(input_json.strip("func_DoSql")))
    elif isinstance(input_json, str):
        res = pattern_all.findall(str(input_json))
        # 对含参数func_xxx{"A":"id"}{"B":"11"} 类型先进行处理
        if res:
            for i in res:
                b = i.split('{')
                merg = b[1:]
                arg_dict = {}
                for j in range(len(merg)):
                    if not merg[j].endswith('}'):
                        merg[j+1] = merg[j] + '{' + merg[j+1]
                        merg[j] = {}
                        continue
                    merg[j] = '{' + merg[j]
                    merg[j] = eval(merg[j])
                    arg_dict.update(merg[j])
                fun_res = eval(b[0])(**arg_dict)
                rereobj = re.compile(i)
                try:
                    if isinstance(fun_res, str) or isinstance(fun_res, int):
                        input_json = rereobj.sub(str(fun_res), input_json)
                    else:
                        input_json = eval(rereobj.sub(str(fun_res), input_json))
                except Exception as e:
                    raise e
        res1 = pattern.findall(str(input_json))
        # 对不含参函数进行处理
        if res1:
            for i in res1:
                fun_res = eval(i)()
                rereobj = re.compile(i)
                if isinstance(fun_res, str) or isinstance(fun_res, int):
                    input_json = rereobj.sub(str(fun_res), input_json)
                else:
                    input_json = eval(rereobj.sub(str(fun_res), input_json))
    elif isinstance(input_json, dict):
        for key in input_json.keys():
            key_value = input_json.get(key)
            key_value = find_func(key_value)
            dic1 = {key: key_value}
            input_json.update(**dic1)
    elif isinstance(input_json, list):
        for json_array in input_json:
            index = input_json.index(json_array)
            input_json[index] = find_func(json_array)
    return input_json


class To:
    """
    用于遍历所有json 的k-v
    """
    @staticmethod
    def get_target_value(dic, tmp_dict=None, parent_nod=None):
        """
        :param parent_nod:
        :param dic: JSON数据
        :param tmp_dict: 用于存储获取的数据
        :return: list
        """
        if not tmp_dict:
            tmp_dict = dict()
        if not isinstance(dic, dict) or not isinstance(tmp_dict, dict):  # 对传入数据进行格式校验
            return 'argv[1] not an dict or argv[-1] not an dict '
        else:
            for key, value in dic.items():  # 传入数据不符合则对其value值进行遍历
                if isinstance(value, dict):
                    tmp_dict[key] = value
                    To.get_target_value(value, tmp_dict=tmp_dict, parent_nod=key)  # 传入数据的value值是字典，则直接调用自身
                elif isinstance(value, (list, tuple)):
                    tmp_dict[key] = value
                    To._get_value(value, tmp_dict=tmp_dict, parent_nod=key)  # 传入数据的value值是列表或者元组，则调用_get_value
                else:
                    if parent_nod:
                        tmp_dict[parent_nod + "_" + key] = value
                    else:
                        tmp_dict[key] = value
        return tmp_dict

    @staticmethod
    def _get_value(val, tmp_dict, parent_nod):
        for val_ in val:
            if isinstance(val_, dict):
                To.get_target_value(val_, tmp_dict=tmp_dict, parent_nod=parent_nod + "_" + str(
                    val.index(val_)))  # 传入数据的value值是字典，则调用get_target_value
            elif isinstance(val_, (list, tuple)):
                To._get_value(val_, tmp_dict=tmp_dict,
                              parent_nod=parent_nod + "_" + str(val.index(val_)))  # 传入数据的value值是列表或者元组，则调用自身
            else:
                index_dic = {parent_nod + "_" + str(val.index(val_)): val_}
                To.get_target_value(val_, tmp_dict=tmp_dict.update(**index_dic),
                                    parent_nod=parent_nod + "_" + str(val.index(val_)))


if __name__ == '__main__':
    pass
