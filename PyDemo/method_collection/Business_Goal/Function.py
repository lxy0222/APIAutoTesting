from comm.script.writeLogs import logger
from PyDemo.method_collection import request_in_a_function
from comm.unit.GlobalVariable import GlobalData


def func_demo_function_name(**kwargs):
    # dicts are lists of information set as global variables
    # {"name": "Variable name", "jsonpath": "jsonpath expression"}
    # tips: 1.You can also set global variables before executing the current function if necessary
    #         setattr(GlobalData.local_data.namespace, "variable name", "variable value")
    #       2.You can also modify the input keyword parameters(kwargs)
    #         and then pass the parameters into request_in_a_function

    dicts = [{"name": "GD_userName", "jsonpath": "$..userName"},
             {"name": "GD_userId", "jsonpath": "$..userId"}]
    request_in_a_function(r"UserManagement/User/test_user_add.yaml", "UserAdd2",
                          "create_user_with_specified_license[PortfolioUser]_and_security_group", dicts, **kwargs)


