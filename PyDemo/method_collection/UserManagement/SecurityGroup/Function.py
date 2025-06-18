
from comm.script.writeLogs import logger

from comm.unit.GlobalVariable import GlobalData
from comm.unit.apiSend import send_request
from comm.unit.initializePremiseData import init_premise, read_json
from config import *

base_url = AC[PROJECT_NAME]["host"]
def update_json(dic_json, key_words):
    for key, value in dic_json.items():
        if key in key_words:
            dic_json[key] = key_words[key]
            del key_words[key]
            if len(key_words) == 0:
                break
        elif isinstance(value, dict):
            update_json(value, key_words)
            if len(key_words) == 0:
                break
    return dic_json

def func_create_security_group(**kwargs):
    from comm.unit.initializePremiseData import init_premise
    case_yaml = os.path.join(os.path.abspath(__file__).strip("registerFunction.py").replace('method_collection', 'page'),"UserManagement/SecurityGroup/test_security_group_add.yaml")
    print(os.path.join(os.path.abspath(__file__).strip("registerFunction.py").replace('method_collection', 'page'),
                       "UserManagement/SecurityGroup/test_security_group_add.yaml"))
    case_path = os.path.dirname(case_yaml)
    case_dict = read_yaml_data(case_yaml)
    data = update_json(case_dict["test_case"][0], kwargs)
    # 初始化请求：执行前置接口+替换关联变量
    test_info, case_data = init_premise(case_dict["test_info"], data, case_path)
    # 发送当前接口
    code, data = send_request(test_info, case_data)
    try:
        GlobalData.local_data.namespace.GD_sgId = data["id"]
    except:
        logger.error("can not get security group id!")
