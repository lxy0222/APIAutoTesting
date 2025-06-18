import allure

from comm.script.writeLogs import logger
import os
import jsonpath
from comm.unit.GlobalVariable import GlobalData
from comm.unit.apiSend import send_request
from comm.utils.databaseExecute import Database
from comm.utils.readJson import update_json
from comm.utils.readYaml import read_yaml_data


def request_in_a_function(caseYaml_path, case_key, request_desc, usePremise=True, useFunction=True, setGloable=None, replace_info=False,
                          new_path='', **kwargs):
    from comm.unit.initializePremiseData import init_premise, read_json
    case_yaml = os.path.join(os.path.abspath(__file__)).replace('method_collection', 'page').replace(
        "__init__.py", rf"{caseYaml_path}")
    logger.debug("case yaml file path:" + case_yaml)
    case_path = os.path.dirname(case_yaml)
    case_dict = read_yaml_data(case_yaml)
    case_datas = [my_dict for my_dict in case_dict['test_case'] if "summary" in my_dict and my_dict["summary"] == case_key][0]
    parameter = read_json(case_datas["summary"], case_datas["parameter"], case_path)
    case_datas["parameter"] = parameter
    case_datas = update_json(case_datas, kwargs)
    if replace_info:
        case_dict["test_info"] = update_json(case_dict["test_info"], kwargs)
    case_dict["test_info"]["setup"] = False
    if new_path:
        case_datas["address"] = new_path
    if usePremise is False:
        case_datas["premise"] = False
    if useFunction is False:
        case_datas["setup_function"] = False
    test_info, case_data, relevance = init_premise(case_dict["test_info"], case_datas, case_path)
    code, data = send_request(test_info, case_data, request_desc)

    if setGloable:
        try:
            for item in setGloable:
                value = jsonpath.jsonpath(data, f"{item['jsonpath']}")[0]
                setattr(GlobalData.local_data.namespace, f"{item['name']}", value)
        except Exception as e:
            logger.error("Failed to set global variables!")
            logger.error(e)
    return code, data


def excute_sql(sql):
    allure.attach(name=f"执行sql", body=str(sql))
    result = Database().execute(sql)
    allure.attach(name=f"执行结果", body=str(result))
    setattr(GlobalData.local_data.namespace, result, result)


def query_sql(select_cols, table, filters):
    Database().query(table, filters, select_cols)
    # setattr(GlobalData.local_data.namespace, result, result)

