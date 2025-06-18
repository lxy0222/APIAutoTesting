import jsonpath
import pytest

from comm.unit import apiSend, replaceRelevance
from comm.unit.initializePremiseData import merge_pre_and_current_params, process_pre_test_info, process_pre_parameter, \
    read_json, call_functions
from comm.utils import readYaml
from comm.utils.readJson import update_json
from config import RC, AC, PROJECT_NAME, PAGE_DIR, API_CONFIG


def pytest_collection_modifyitems(items):
    for item in items:
        name = item.name
        cls_name = item.parent.parent.name
        # 如果该测试类在 skip_classes 中，跳过该测试项
        if RC['skip_classes']:
            if cls_name in RC['skip_classes']:
                item.add_marker(pytest.mark.skip(reason="skip class"))
        if RC['skip_methods']:
            if cls_name in RC['skip_methods'].keys():
                if name.split("[")[0] in RC['skip_methods'].get(cls_name, []):
                    item.add_marker(pytest.mark.skip(reason="skip method"))


@pytest.fixture(scope="class", autouse=False)
def class_setup_and_teardown_fixture(request):
    __relevanceMer = {}
    aconfig = readYaml.read_yaml_data(API_CONFIG)

    def process_premise(premise_data, isTeardown=False):
        __relevance = aconfig[PROJECT_NAME]
        for data in premise_data:
            case_path = PAGE_DIR + data[0]
            case_data = readYaml.read_yaml_data(case_path)
            case = [my_dict for my_dict in case_data["test_case"] if "summary" in my_dict and my_dict["summary"] == data[1]][0]
            test_info = update_json(case_data['test_info'], data[3])
            case = update_json(case, data[3])
            test_info = process_pre_test_info(test_info, __relevance)
            parameter = read_json(case['summary'], case['parameter'], case_path)
            parameter = replaceRelevance.replace(parameter, __relevance)
            case['parameter'] = parameter

            if isTeardown:
                response, res = apiSend.send_request(test_info, case, data[2])
                continue

            if "premise" in case_data["test_case"]:
                sub_premise = case_data["test_case"]["premise"]
                __relevanceMer.update(__relevance)
                process_premise(sub_premise)
            response, res = apiSend.send_request(test_info, case, data[2])
            __relevance = merge_pre_and_current_params(case, res, __relevance, data[4])
            __relevanceMer.update(__relevance)

    test_data = request.cls.param_value
    premise_list = test_data["setup"].get('premise', False)
    if premise_list:
        process_premise(premise_list)
    # setup_function
    setup_function = test_data["setup"].get('function', False)
    if setup_function:
        call_functions(**setup_function)
    request.cls.response_data = __relevanceMer

    yield
    test_data["teardown"] = replaceRelevance.replace(test_data["teardown"], __relevanceMer)

    if test_data["teardown"].get('function', False):
        # 执行当前测试用例的数据清理操作
        call_functions(**test_data["teardown"]["function"])
    if test_data["teardown"].get('premise', False):
        # 执行当前测试用例的数据清理操作
        process_premise(test_data["teardown"]["premise"], isTeardown=True)
