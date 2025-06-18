# -*- coding:utf-8 -*-
# @Time    : 2021/07/10
# @Author  : Xuanyu Liu
# @File    : initializePremise.py
# **************************
import time
from json import JSONDecodeError
from comm.unit.initializeFunc import *
from comm.utils.readJson import update_json
from config import PAGE_DIR, PROJECT_NAME, API_CONFIG
from comm.unit import apiSend, readRelevance, replaceRelevance
from comm.utils import readYaml
from typing import Optional
from PyDemo.method_collection.registerFunction import call_function


def init_premise(test_info, case_data, case_path, relevance=None):
    # 获取项目公共关联值
    if relevance is None:
        relevance = {}
    aconfig = readYaml.read_yaml_data(API_CONFIG)
    __relevance = dict(relevance, **aconfig[PROJECT_NAME])

    # 判断是否有前置接口 如果有就执行
    __relevanceMer = execute_pre_cases(test_info, case_data, case_data["title"], __relevance)
    # 判断是否需要调用其他方法
    call_setup_function(case_data, __relevanceMer)
    # 处理当前接口
    parameter = read_json(case_data['summary'], case_data['parameter'], case_path)
    case_data['parameter'] = parameter
    case_data = replaceRelevance.replace(case_data, __relevanceMer)
    logger.debug("请求参数处理结果：{}".format(case_data['parameter']))

    # 处理test_info信息
    test_info = replaceRelevance.replace(test_info, __relevanceMer)
    logger.debug("测试信息处理结果：{}".format(test_info))

    # 获取当前接口期望结果：获取期望结果-获取关联值-替换关联值
    expected_rs = read_json(case_data['summary'], case_data['check_body']['expected_result'], case_path)
    __relevanceMer = readRelevance.get_relevance(parameter, expected_rs, __relevanceMer)
    expected_rs = replaceRelevance.replace(expected_rs, __relevanceMer)
    case_data['check_body']['expected_result'] = expected_rs
    logger.debug("期望返回处理结果：{}".format(case_data['check_body']['expected_result']))

    # 处理teardown info
    teardown_class = read_json(case_data['summary'], test_info['clean_up'], case_path)
    teardown_function = read_json(case_data['summary'], case_data['clean_up'], case_path)
    teardown_class = replaceRelevance.replace(teardown_class, __relevanceMer)
    teardown_function = replaceRelevance.replace(teardown_function, __relevanceMer)
    test_info['clean_up'] = teardown_class
    case_data['clean_up'] = teardown_function
    logger.debug(
        "数据清理参数处理结果：class level-{}；function level".format(test_info['clean_up'], case_data['clean_up']))

    return test_info, case_data


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
            with open(case_path + '/' + json_obj, "r", encoding="utf-8") as js:
                data_list = json.load(js)
                for data in data_list:
                    if data['summary'] == summary:
                        return data['body']
        except FileNotFoundError:
            raise Exception("用例关联文件不存在\n文件路径： %s" % json_obj)
        except JSONDecodeError as e:
            raise Exception(f"用例关联的文件有误\n文件路径： {json_obj},错误信息：{e}")


def call_functions(**kwargs):
    """用于处理setup method的函数调用
    :param kwargs: setup_method 参数值
    :return:
    """

    for func_name, func_args in kwargs.items():
        call_function(func_name, **func_args)


def call_setup_function(case_data, relevance):
    setup_function = case_data.get("setup_function", None)
    if setup_function:
        setup_function = replaceRelevance.replace(setup_function, relevance)
        call_functions(**setup_function)


def process_pre_test_info(pre_test_info, relevance):
    pre_test_info = replaceRelevance.replace(pre_test_info, relevance)
    logger.debug("测试信息处理结果：{}".format(pre_test_info))
    return pre_test_info


def process_pre_parameter(pre_case_data, pre_case_path, relevance):
    if pre_case_path.endswith(".yaml"):
        pre_case_path = os.path.dirname(pre_case_path)
    pre_parameter = read_json(pre_case_data['summary'], pre_case_data['parameter'], pre_case_path)
    pre_parameter = replaceRelevance.replace(pre_parameter, relevance)
    pre_case_data['parameter'] = pre_parameter
    logger.debug("请求参数处理结果：{}".format(pre_parameter))
    return pre_parameter


def merge_pre_and_current_params(pre_parameter, response_data, relevance, flag=''):
    pre_parameter_req = JsonTraverser.traverse_json(pre_parameter, flag="req" + flag)
    pre_parameter_res = JsonTraverser.traverse_json(response_data, flag="res" + flag)
    toData = dict(pre_parameter_req, **pre_parameter_res)
    __relevanceMer = dict(relevance, **toData)
    return __relevanceMer


# def execute_pre_case(test_info, case_data, relevance):
#     """
#     Execute pre-test cases for the current test case.
#     :param case_data: the data for the current test case
#     :param test_info: the info for the current test case
#     :param relevance: the current relevance parameters
#     :return: the updated relevance parameters
#     """
#     premise_list = case_data.get("premise", test_info.get("premise", []))
#     __relevanceMer = relevance  # initialize with the current relevance
#     for index, premise in enumerate(premise_list):
#         pre_test_info, pre_case_data, pre_case_path, replace_kw, premise_desc = get_pre_case_data_1(premise)
#         if not pre_case_data:
#             continue
#
#         for i in range(3):
#             logger.info("Executing pre-test case: {}".format(pre_test_info))
#             pre_test_info = update_json(pre_test_info, replace_kw)
#             pre_case_data = update_json(pre_case_data, replace_kw)
#             pre_test_info = process_pre_test_info(pre_test_info, __relevanceMer)
#             pre_parameter = process_pre_parameter(pre_case_data, pre_case_path, __relevanceMer)
#             response, data = apiSend.send_request(pre_test_info, pre_case_data, premise_desc)
#             if response.status_code >= 300:
#                 time.sleep(1)
#                 logger.error("Pre-test case request failed! Waiting 1 second before retrying!")
#                 continue
#             __relevanceMer = merge_pre_and_current_params(pre_parameter, data, __relevanceMer, flag=str(index))
#
#             break
#         else:
#             logger.info("Pre-test case request failed! Tried 3 times and failed!")
#             raise Exception("Failed to get relevant data from pre-test cases!")
#
#     return __relevanceMer

# def get_pre_case_data_1(premise):
#     # premise = case_data.get("premise", test_info.get("premise", False))
#     if premise:
#         # conf_list = premise.split(" ")
#         pre_case_path = PAGE_DIR + premise[0]
#         premise_desc = premise[2]
#         replace_kw = {}
#         if len(premise) == 4:
#             replace_kw = premise[3]
#         # 获取前置接口用例
#         logger.info("获取前置接口测试用例：{}".format(pre_case_path))
#         # 拿到测试用例具体case
#         pre_case_dict = readYaml.read_yaml_data(pre_case_path)
#         pre_test_info = pre_case_dict['test_info']
#         pre_case_data = [my_dict for my_dict in pre_case_dict['test_case'] if
#                          "summary" in my_dict and my_dict["summary"] == premise[1]][0]
#         # 判断前置接口是否也存在前置接口
#         # if pre_case_data["premise"]:
#         #     pre_case_path = os.path.dirname(pre_case_path)
#         #     init_premise(pre_test_info, pre_case_data, pre_case_path)
#         return pre_test_info, pre_case_data, pre_case_path, replace_kw, premise_desc
#     else:
#         return None, None, None, None, None
def execute_pre_cases(test_info, case_data, case_desc, relevance=None, pre_results=None, replace_kw=None, flag=''):
    __relevanceMer = relevance
    case_path = ""
    if pre_results is None:
        pre_results = {}

    # 如果前置用例有前置用例，则递归执行前置用例的前置用例
    if case_data.get('premise'):
        for pre_pre_case in case_data['premise']:
            case_path = PAGE_DIR+pre_pre_case[0]
            case_data = readYaml.read_yaml_data(case_path)
            relevance = execute_pre_cases(case_data["test_info"], [my_dict for my_dict in case_data["test_case"] if
                         "summary" in my_dict and my_dict["summary"] == pre_pre_case[1]][0], pre_pre_case[2], relevance, pre_results,pre_pre_case[3], flag=pre_pre_case[4])
            __relevanceMer.update(relevance)
    # 执行当前前置用例
    pre_case_path = case_path
    pre_test_info = test_info
    pre_case_data = case_data
    premise_desc = case_desc
    replace_kw = replace_kw

    logger.info("执行前置接口测试用例：{}".format(pre_test_info))
    pre_test_info = update_json(pre_test_info, replace_kw)
    pre_case_data = update_json(pre_case_data, replace_kw)
    pre_test_info = process_pre_test_info(pre_test_info, __relevanceMer)
    pre_parameter = process_pre_parameter(pre_case_data, pre_case_path, __relevanceMer)
    response, data = apiSend.send_request(pre_test_info, pre_case_data, premise_desc)

    # # 将当前前置用例的执行结果存储在字典中
    # pre_name = pre_test_info['name']
    # pre_results[pre_name] = {'request': pre_case_data, 'response': response}

    # 将当前前置用例的响应结果合并到 __relevanceMer 中
    __relevanceMer = merge_pre_and_current_params(pre_parameter, data, __relevanceMer, flag)

    return __relevanceMer


class JsonTraverser:
    """
    Used to traverse all the key-value pairs in a JSON object.
    """

    @staticmethod
    def traverse_json(dic: dict, flag: Optional[str] = '', tmp_dict: Optional[dict] = None,
                      parent_nod: Optional[str] = None) -> dict:
        """
        :param flag:
        :param parent_nod:
        :param dic: JSON data
        :param tmp_dict: Used to store the retrieved data
        :return: dict
        """
        if tmp_dict is None:
            tmp_dict = {}
        for key, value in dic.items():
            if isinstance(value, dict):
                if flag:
                    tmp_dict[f"{flag}_{key}"] = value
                    JsonTraverser.traverse_json(value, flag=flag, tmp_dict=tmp_dict, parent_nod=key)
                else:
                    tmp_dict[key] = value
                    JsonTraverser.traverse_json(value, tmp_dict=tmp_dict, parent_nod=key)
            elif isinstance(value, (list, tuple)):
                tmp_dict[key] = value
                JsonTraverser._get_value(value, tmp_dict=tmp_dict, parent_nod=key, flag=flag)
            else:
                if parent_nod:
                    if flag:
                        tmp_dict[f"{flag}_{parent_nod}_{key}"] = value
                    else:
                        tmp_dict[f"{parent_nod}_{key}"] = value
                else:
                    if flag:
                        tmp_dict[f"{flag}_{key}"] = value
                    else:
                        tmp_dict[key] = value
        return tmp_dict

    @staticmethod
    def _get_value(val, tmp_dict, parent_nod, flag):
        for i, val_ in enumerate(val):
            if isinstance(val_, dict):
                if flag:
                    JsonTraverser.traverse_json(val_, flag=flag, tmp_dict=tmp_dict, parent_nod=f"{parent_nod}_{i}")
                else:
                    JsonTraverser.traverse_json(val_, tmp_dict=tmp_dict, parent_nod=f"{parent_nod}_{i}")
            elif isinstance(val_, (list, tuple)):
                JsonTraverser._get_value(val_, tmp_dict=tmp_dict, parent_nod=f"{parent_nod}_{i}", flag=flag)
            else:
                if parent_nod:
                    if flag:
                        tmp_dict[f"{flag}_{parent_nod}_{i}"] = val_
                    else:
                        tmp_dict[f"{parent_nod}_{i}"] = val_
                else:
                    if flag:
                        tmp_dict[f"{flag}_{i}"] = val_
                    else:
                        tmp_dict[i] = val_


if __name__ == '__main__':
    pre_parameter_all = JsonTraverser.traverse_json(
        {'data': {'id': 32064, 'managers': [{'userId': 1, 'fullName': 'Admin User'}], 'name': 'ws_ssss'}}, flag="")
    print(pre_parameter_all)
