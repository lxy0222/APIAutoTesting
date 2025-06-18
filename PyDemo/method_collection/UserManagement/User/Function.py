from PyDemo.method_collection import request_in_a_function
from comm.script.writeLogs import logger
from comm.unit.GlobalVariable import GlobalData


def func_create_user_with_specified_license_and_security_group(**kwargs):
    """
    licenses: list[]
    securityGroups: list[]
    """
    license_map = {
        1: {'name': 'DeploymentManagement', 'index': 5, "value": False},
        2: {'name': 'DemandManagement', 'index': 4, "value": False},
        3: {'name': 'ProjectManagement', 'index': 8, "value": False},
        4: {'name': 'ProgramManagement', 'index': 7, "value": False},
        5: {'name': 'TimeManagement', 'index': 9, "value": False},
        6: {'name': 'PortfolioManagement', 'index': 6, "value": False},
        7: {'name': 'UserAdmin', 'index': 1, "value": False},
        8: {'name': 'Configuration', 'index': 0, "value": False},
        12: {'name': 'PortfolioAnalyst', 'index': 2, "value": False},
        13: {'name': 'PortfolioUser', 'index': 3, "value": False}
    }
    try:
        for license in kwargs["licenses"]:
            if license in license_map:
                license_map[license]["value"] = True
        for k, v in license_map.items():
            setattr(GlobalData.local_data.namespace, f"GD_checked_{v['index']}", v['value'])
        noOrgSecurityGroups = [{"meaning": "dummy", "code": code} for code in kwargs["securityGroups"]]
        kwargs["noOrgSecurityGroups"] = noOrgSecurityGroups
        logger.debug("这是kwargs的值")
        logger.debug(kwargs)
    except Exception as e:
        logger.warning("no keyword [licenses] or [securityGroups]!")
        logger.error(e)
    del kwargs["licenses"]
    del kwargs["securityGroups"]
    dicts = [{"name": "GD_userName", "jsonpath": "$..userName"},
             {"name": "GD_userId", "jsonpath": "$..userId"}]

    request_in_a_function(r"UserManagement\User\test_user_add.yaml", "UserAdd2",
                          "create_user_with_specified_license[PortfolioUser]_and_security_group", dicts, **kwargs)


def func_setup_test(**kwargs):
    print("这只是setup的function")
    print(kwargs)
    logger.debug("这只是setup的function")


def func_teardown_test(**kwargs):
    print("这只是teardown的function")
    print(kwargs)
    logger.debug("这只是teardown的function")
