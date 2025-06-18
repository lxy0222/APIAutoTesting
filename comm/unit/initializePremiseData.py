# -*- coding:utf-8 -*-
# @File    : initializePremise.py
# **************************
import json
import os
import time
from json import JSONDecodeError

import allure

from comm.script.writeLogs import logger
from comm.utils.readJson import update_json
from config import PAGE_DIR, PROJECT_NAME, API_CONFIG
from comm.unit import apiSend, readRelevance, replaceRelevance
from comm.utils import readYaml
from typing import Optional
from PyDemo.method_collection.registerFunction import call_function


@allure.step("setup function")
def setup_init(test_info, case_data, __relevance):
    __relevanceMer = execute_pre_cases(test_info, case_data, case_data["title"], __relevance)
    call_setup_function(case_data, __relevanceMer)
    return __relevanceMer


def init_premise(test_info, case_data, case_path, relevance=None):
    if relevance is None:
        relevance = {}
    aconfig = readYaml.read_yaml_data(API_CONFIG)
    __relevance = dict(relevance, **aconfig[PROJECT_NAME])
    __relevanceMer = setup_init(test_info, case_data, __relevance)

    parameter = read_json(case_data['summary'], case_data['parameter'], case_path)
    case_data['parameter'] = parameter
    case_data = replaceRelevance.replace(case_data, __relevanceMer)
    logger.debug("parameter processing result：{}".format(case_data['parameter']))

    test_info = replaceRelevance.replace(test_info, __relevanceMer)
    logger.debug("test info processing result：{}".format(test_info))

    expected_rs = read_json(case_data['summary'], case_data['check_body']['expected_result'], case_path)
    case_data['check_body']['expected_result'] = expected_rs
    # __relevanceMer = readRelevance.get_relevance(parameter, expected_rs, __relevanceMer)
    # expected_rs = replaceRelevance.replace(expected_rs, __relevanceMer)
    logger.debug("desired processing result：{}".format(case_data['check_body']['expected_result']))

    return test_info, case_data, __relevanceMer


def read_json(summary, json_obj, case_path):
    """
    Check content read
    :param summary: Use case name
    :param json_obj: json file or data object
    :param case_path: case path
    :return:
    """
    if isinstance(json_obj, dict) or isinstance(json_obj, list):
        return json_obj
    elif json_obj is None:
        return {}
    else:
        if isinstance(json_obj, str) and json_obj.endswith("json"):
            try:
                with open(case_path + '/' + json_obj, "r", encoding="utf-8") as js:
                    data_list = json.load(js)
                    for data in data_list:
                        if data['summary'] == summary:
                            return data['body']
            except FileNotFoundError:
                raise Exception("Case association file does not exist \n file path: %s： %s" % json_obj)
            except JSONDecodeError as e:
                raise Exception(f"The file associated with the case is the wrong \n file path： {json_obj},error：{e}")
        else:
            return json_obj


def call_functions(**kwargs):
    """ is used to handle function calls for setup method

    :param kwargs: setup_method Specifies the value of the parameter
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
    logger.debug("test info processing result：{}".format(pre_test_info))
    return pre_test_info


def process_pre_parameter(pre_case_data, pre_case_path, relevance):
    if pre_case_path.endswith(".yaml"):
        pre_case_path = os.path.dirname(pre_case_path)
    pre_parameter = read_json(pre_case_data['summary'], pre_case_data['parameter'], pre_case_path)
    pre_parameter = replaceRelevance.replace(pre_parameter, relevance)
    pre_case_data['parameter'] = pre_parameter
    logger.debug("parameter processing result：{}".format(pre_parameter))
    return pre_parameter


def merge_pre_and_current_params(pre_parameter, response_data, relevance, flag=''):
    pre_parameter_req = JsonTraverser.traverse_json(pre_parameter, flag="req" + flag)
    pre_parameter_res = JsonTraverser.traverse_json(response_data, flag="res" + flag)
    toData = dict(pre_parameter_req, **pre_parameter_res)
    __relevanceMer = dict(relevance, **toData)
    return __relevanceMer


def execute_pre_cases(test_info, case_data, case_desc, relevance=None, pre_results=None, replace_kw=None, flag='', executed_cases=None, case_path=''):
    if executed_cases is None:
        executed_cases = []  # Used to track the leading use cases that have been executed

    relevance_mer = relevance
    if pre_results is None:
        pre_results = {}

    case_key = (test_info, case_data, case_desc, relevance, flag)
    if case_key in [item[0] for item in executed_cases]:
        # If the preceding use case has already been executed, simply return an empty association result
        return relevance_mer

    executed_cases.append((case_key,))  # Adds key information about the current use case to the executed list


    # The preceding use case of the current use case is executed first
    if case_data.get('premise'):
        for pre_pre_case in case_data['premise']:
            pre_case_path = PAGE_DIR + pre_pre_case[0]
            pre_case_data = readYaml.read_yaml_data(pre_case_path)

            pre_test_info = pre_case_data.get("test_info", {})
            pre_test_case = next((my_dict for my_dict in pre_case_data.get("test_case", []) if
                                  "summary" in my_dict and my_dict["summary"] == pre_pre_case[1]), None)
            pre_case_desc = pre_pre_case[2]
            pre_replace_kw = pre_pre_case[3]
            pre_flag = pre_pre_case[4]

            relevance = execute_pre_cases(pre_test_info, pre_test_case, pre_case_desc, relevance,
                                          pre_results, pre_replace_kw, flag=pre_flag,
                                          executed_cases=executed_cases, case_path=pre_case_path)
            relevance_mer.update(relevance)

    pre_case_path = case_path
    pre_test_info = test_info
    premise_desc = case_desc
    replace_kw = replace_kw

    if len(pre_case_path) != 0:
        logger.info("Execute the front interface test case：{}".format(pre_test_info))
        pre_test_info = update_json(pre_test_info, replace_kw)
        case_data["parameter"] = read_json(case_data['summary'], case_data['parameter'], os.path.dirname(pre_case_path))
        case_data = update_json(case_data, replace_kw)
        pre_test_info = process_pre_test_info(pre_test_info, relevance_mer)
        pre_parameter = process_pre_parameter(case_data, pre_case_path, relevance_mer)
        response, data = apiSend.send_request(pre_test_info, case_data, premise_desc)

        relevance_mer = merge_pre_and_current_params(pre_parameter, data, relevance_mer, flag)

    executed_cases.pop()  # After executing the current use case, remove the key information about the current use case
    # from the executed list

    return relevance_mer


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
