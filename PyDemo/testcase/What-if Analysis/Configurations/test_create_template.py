# -*- coding:utf-8 -*-
# @File    : test_TemplateCreate.py
# ****************************
from comm.script.writeLogs import logger
import os
import allure
import pytest

from comm.unit import replaceRelevance, apiSend
from comm.utils import readYaml
from comm.utils.readJson import update_json
from comm.utils.readYaml import read_yaml_data
from comm.unit.initializePremiseData import init_premise, merge_pre_and_current_params, \
    process_pre_test_info, read_json, call_functions
from comm.unit.apiSend import send_request
from comm.unit.checkResult import check_result, check_by_request
from config import PAGE_DIR

case_yaml = os.path.realpath(__file__).replace('testcase', 'page').replace('.py', '.yaml')
case_path = os.path.dirname(case_yaml)
case_dict = read_yaml_data(case_yaml)


@allure.epic(case_dict["test_info"]["epic"])
@allure.feature(case_dict["test_info"]["feature"])
@pytest.mark.usefixtures("class_setup_and_teardown_fixture")
class TestConfiguration:
    param_value = case_dict["test_info"]  # 定义传递给 fixture 的参数

    @allure.title("{case_data[title]}")
    @pytest.mark.parametrize("case_data", case_dict["test_case"])
    @allure.story("TemplateCreate")
    def test_TemplateCreate(self, case_data):
        des = f"""
        <h1>{case_data["title"]}</h1>
        <table style="width:100%" border="1">
            <tbody>
                <tr>
                    <th>Description</th>
                    <td>{case_data['describe']["Description"]}</td>
                </tr>
                <tr>
                    <th>Function Designer</th>
                    <td>{case_data['describe']["FunctionDesigner"]}</td>
                </tr>
                <tr>
                    <th>Author</th>
                    <td>{case_data['describe']["Author"]}</td>
                </tr>
                <tr>
                    <th>Create Date</th>
                    <td>{case_data['describe']["CreateDate"]}</td>
                </tr>
            </tbody>
        </table>
        """
        if case_data.get('skip', False):
            pytest.skip('This test is skipped.')
        allure.dynamic.description_html(des)
        allure.dynamic.tag(case_data['tag'])
        allure.dynamic.issue(case_data['issue'])
        # 初始化请求：执行前置接口+替换关联变量
        test_info, case_data, relevance = init_premise(case_dict["test_info"], case_data, case_path, self.response_data)
        # 发送当前接口
        res, data = send_request(test_info, case_data)
        # 替换期待值
        relevance = merge_pre_and_current_params(case_data["parameter"], data, relevance, "")
        expected_rs = replaceRelevance.replace(case_data['check_body'], relevance)
        case_data['check_body'] = expected_rs
        # 校验接口返回
        try:
            check_result(case_data, res.status_code, data)
            case_info_copy = case_dict["test_info"].copy()
            case_data_copy = case_data.copy()
            relevance_copy = relevance
            data_copy = data
            check_by_request(case_info_copy, case_data_copy, data_copy, relevance_copy)

        except Exception as e:
            logger.debug(e)
            raise e
        finally:
            self.res_data = data
            self.req_data = case_data['parameter']
            teardown_case(case_data, data, self.response_data)


@allure.step("teardown function")
def teardown_case(case_data, response_data, relevance):
    data = response_data
    __relevanceMer = merge_pre_and_current_params(case_data['parameter'], data, relevance)
    case_data["teardown"] = replaceRelevance.replace(case_data["teardown"], __relevanceMer)
    if case_data["teardown"].get('premise', False):
        # 执行当前测试用例的数据清理操作
        for td in case_data["teardown"]["premise"]:
            case_path1 = PAGE_DIR + td[0]
            case_data1 = readYaml.read_yaml_data(case_path1)
            case = [my_dict for my_dict in case_data1["test_case"] if
                    "summary" in my_dict and my_dict["summary"] == td[1]][0]
            test_info = update_json(case_data1['test_info'], td[3])
            case = update_json(case, td[3])
            test_info = process_pre_test_info(test_info, __relevanceMer)
            parameter = read_json(case['summary'], case['parameter'], case_path1)
            parameter = replaceRelevance.replace(parameter, __relevanceMer)
            case['parameter'] = parameter
            response, res = apiSend.send_request(test_info, case, td[2])
    if case_data["teardown"].get('function', False):
        # 执行当前测试用例的数据清理操作
        call_functions(**case_data["teardown"]["function"])