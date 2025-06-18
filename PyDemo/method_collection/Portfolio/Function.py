import time

import jsonpath

from comm.script.writeLogs import logger
from PyDemo.method_collection import request_in_a_function
from comm.unit.GlobalVariable import GlobalData
from comm.utils.SoapParser import xml_to_dict, SoapParser
from comm.utils.databaseExecute import Database
from comm.utils.randomly import *
from config import PROJECT_NAME, AC


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


def create_data(hierarchy):
    """
    input_data = {
        "type": "portfolio",
        "name": "ws_TOP_portfolio",
        "strategicThemes": [
            {
                "name": "Top_st",
                "parent": "",
                "color": "#6890CB",
                "children": [],
                "businessGoals": []
            }
        ],
        "children": [
            {
                "type": "portfolio",
                "name": "ws_sub_portfolio1",
                "children": [
                    {
                        "type": "portfolio",
                        "name": "ws_sub_sub_portfolio1",
                        "children": []
                    },
                    {
                        "type": "proposal",
                        "name": "nested_proposal"
                    }
                ]
            },
            {
                "type": "proposal",
                "name": "ws_proposal"
            },
            {
                "type": "program",
                "name": "ws_program"
            }
        ]
    }
    """
    def create_node(name, type, parent):
        node = {
            "name": name,
            "type": type,
            "parent": parent,
            "children": []
        }
        timestamp = generate_timestamp()
        # 根据类型调用不同的接口
        if node["type"] == "portfolio":
            dicts = [{"name": f"GD_{name}_name", "jsonpath": "$..name"},
                     {"name": f"GD_{name}_id", "jsonpath": "$..id"}]
            code, data = request_in_a_function(r"/Portfolio/test_portfolio_create.yaml", "Create a portfolio",
                                  "create portfolio", setGloable=dicts, name=name+str(timestamp))

            if parent is not None:
                code, data = request_in_a_function(r"/Portfolio/PortfolioContent/test_content_add.yaml",
                                                   "Add a sub-portfolio to portfolio", f"Add ", usePremise=False,
                                                   new_path="/itg/rest2/portfolios/${" + f"GD_{parent['name']}_id" + "}/contents/subPortfolios",
                                                   childPortfolioId=data["data"]['id'])
        # 调用与portfolio相关的接口
        # ...
        elif node["type"] == "proposal":
            dicts = [{"name": f"GD_{name}_name", "jsonpath": "$..name"},
                     {"name": f"GD_{name}_id", "jsonpath": "$..id"}]
            code, data = request_in_a_function(r"/proposal/proposal_create.yaml", "Create a proposal",
                                  "create proposal", setGloable=dicts, kwargs={"$..*[?(@.token=='REQ.DESCRIPTION')].stringValue":name+str(timestamp),
                                                                               "$..*[?(@.token=='REQ.KNTA_PROJECT_NAME')].stringValue":name+str(timestamp)})
            # # 进行与parent关联的操作
            if parent is not None:
                    code, data = request_in_a_function(r"/Portfolio/portfolio_api.yaml", "Get fsId by ppaId",
                                          f"Get fsId [{data['ns2:request']['id']}]",
                                          kwargs={"fm:parentType": node["type"].upper(), "fm:id": data['ns2:request']['id']})
                    # data = xml_to_dict(data)
                    fsId = SoapParser().get_first_element_body_by_name(data, "id")
                    code, data = request_in_a_function(r"/Portfolio/portfolio_api.yaml", "Add ppa to portfolio",
                                          f"Add ppa [{node['type']}:{name}] to portfolio", new_path="/itg/rest2/portfolios/${" + f"GD_{node['parent']['name']}_id" + "}/contents/ppas",
                                          fsId=fsId)

        elif node["type"] == "program":
            code, data = request_in_a_function(r"/Portfolio/portfolio_api.yaml", "create a program by soap",
                                               f"create a program [{node['name']}] by soap api ",
                                               kwargs={"ns1:name": node["name"] + str(timestamp)})
            programId = SoapParser().get_first_element_body_by_name(data, "programId")
            setattr(GlobalData.local_data.namespace, f"GD_{node['name']}_id", programId)
            code, data = request_in_a_function(r"/Portfolio/portfolio_api.yaml", "update program to enable add to portfolio",
                                               f"update program to enable add to portfolio ", id=programId)
            code, data = request_in_a_function(r"/Portfolio/portfolio_api.yaml",
                                               "add program to portfolio without update program setting",
                                               f"add program to portfolio without update program setting ",
                                               new_path="/itg/rest2/portfolios/${" + f"GD_{node['parent']['name']}_id" + "}/contents/programs",
                                               programId=programId)
        return node

    def add_child(parent, child):
        parent["children"].append(child)

    def create_hierarchy(data, parent=None):
        node = create_node(data["name"], data["type"], parent)

        if parent is not None:
            add_child(parent, node)

        for child_data in data.get("children", []):
            create_hierarchy(child_data, node)

        return node


    # 创建层级结构并关联
    hierarchy = create_hierarchy(hierarchy)


def batch_create_data():
    input_data = {
        "type": "portfolio",
        "name": "ws_TOP_ADM",
        "children": [
            {
                "type": "portfolio",
                "name": "ws_sub_PPM",
                "children": [
                    {
                        "type": "program",
                        "name": "ws_sub_PGM"
                    }
                ]
            },
            {
                "type": "program",
                "name": "ws_PGM"
            }
        ]
    }
    # create tree
    create_data(input_data)


import threading
fsId_list = []
project_list = []
proposal_list = []
project_dict = {}
proposal_dict = {}

def call_method(type_need):
    month = "January,February,March,April,May,June,July,August,September,October,November,December"
    if type_need == "proposal":
        startDate = random_choice(month) + ' ' + str(generate_year())
        endDate = random_choice(month) + ' ' + str(generate_year('y+1'))
        proposal_name = "ws_proposal_"+random_str(16)
        code, data = request_in_a_function(r"/proposal/proposal_create.yaml", "Create a proposal",
                                           "create proposal",
                                           kwargs={"$..*[?(@.token=='REQ.DESCRIPTION')].stringValue": proposal_name,
                                                   "$..*[?(@.token=='REQ.KNTA_PROJECT_NAME')].stringValue": proposal_name,
                                                   "$..*[?(@.token=='REQ.KNTA_PLAN_FINISH_DATE')].stringValue": endDate,
                                                   "$..*[?(@.token=='REQ.KNTA_PLAN_START_DATE')].stringValue": startDate})
        proposal_Id = data['ns2:request']['id']
        code, data = request_in_a_function(r"/Portfolio/portfolio_api.yaml", "Get fsId by ppaId",
                                           f"Get fsId",
                                           kwargs={"fm:parentType": "PROPOSAL".upper(),
                                                   "fm:id": proposal_Id})
        fsId = SoapParser().get_first_element_body_by_name(data, "id")

        code, data = request_in_a_function(r"/Portfolio/portfolio_api.yaml",
                                           "update financial summary with CapexOpex enabled",
                                           f"update financial summary with CapexOpex enabled",
                                           replace_info=True,
                                           headers={"SOAPAction": "urn:updateFinancialSummary"},
                                           parameter=f'<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"> <soapenv:Header/> <soapenv:Body> <service:readFinancialSummaryResponse xmlns="http://mercury.com/ppm/fm/1.0" xmlns:service="http://mercury.com/ppm/fm/service/1.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"> <service:financialSummary> <id>{fsId}</id> <name>{proposal_name}</name> <parent> <parentType>PROPOSAL</parentType> <parentIdentifier> <id>{proposal_Id}</id> <name>{proposal_name}</name> </parentIdentifier> </parent> <localCurrencyCode>USD</localCurrencyCode> <baseCurrencyCode>USD</baseCurrencyCode> <approvedBudgets/> <forecastActual> <isCapexOpexEnabled>true</isCapexOpexEnabled> <actualRollupCode>MANUAL</actualRollupCode> <lines> <line> <expenseType>Capital</expenseType> <laborType>Labor</laborType> <category>Contractor</category> <syncSourceCode>NO_SYNC</syncSourceCode> <editable>true</editable> <cells> <cell> <period> <periodStartDate>2023-01-01</periodStartDate> <periodType>MONTH</periodType> </period> <actualValueBSE>300</actualValueBSE> <actualValueLCL>300</actualValueLCL> <planValueBSE>1000</planValueBSE> <planValueLCL>1000</planValueLCL> </cell> <cell> <period> <periodStartDate>2023-02-01</periodStartDate> <periodType>MONTH</periodType> </period> <actualValueBSE>300</actualValueBSE> <actualValueLCL>300</actualValueLCL> <planValueBSE>1000</planValueBSE> <planValueLCL>1000</planValueLCL> </cell> <cell> <period> <periodStartDate>2023-03-01</periodStartDate> <periodType>MONTH</periodType> </period> <actualValueBSE>300</actualValueBSE> <actualValueLCL>300</actualValueLCL> <planValueBSE>1000</planValueBSE> <planValueLCL>1000</planValueLCL> </cell> <cell> <period> <periodStartDate>2023-04-01</periodStartDate> <periodType>MONTH</periodType> </period> <actualValueBSE>300</actualValueBSE> <actualValueLCL>300</actualValueLCL> <planValueBSE>1000</planValueBSE> <planValueLCL>1000</planValueLCL> </cell> <cell> <period> <periodStartDate>2023-05-01</periodStartDate> <periodType>MONTH</periodType> </period> <actualValueBSE>300</actualValueBSE> <actualValueLCL>300</actualValueLCL> <planValueBSE>1000</planValueBSE> <planValueLCL>1000</planValueLCL> </cell> <cell> <period> <periodStartDate>2023-06-01</periodStartDate> <periodType>MONTH</periodType> </period> <actualValueBSE>300</actualValueBSE> <actualValueLCL>300</actualValueLCL> <planValueBSE>1000</planValueBSE> <planValueLCL>1000</planValueLCL> </cell> <cell> <period> <periodStartDate>2023-07-01</periodStartDate> <periodType>MONTH</periodType> </period> <actualValueBSE>300</actualValueBSE> <actualValueLCL>300</actualValueLCL> <planValueBSE>1000</planValueBSE> <planValueLCL>1000</planValueLCL> </cell> <cell> <period> <periodStartDate>2023-08-01</periodStartDate> <periodType>MONTH</periodType> </period> <actualValueBSE>300</actualValueBSE> <actualValueLCL>300</actualValueLCL> <planValueBSE>1000</planValueBSE> <planValueLCL>1000</planValueLCL> </cell> <cell> <period> <periodStartDate>2023-09-01</periodStartDate> <periodType>MONTH</periodType> </period> <actualValueBSE>300</actualValueBSE> <actualValueLCL>300</actualValueLCL> <planValueBSE>1000</planValueBSE> <planValueLCL>1000</planValueLCL> </cell> <cell> <period> <periodStartDate>2023-10-01</periodStartDate> <periodType>MONTH</periodType> </period> <actualValueBSE>300</actualValueBSE> <actualValueLCL>300</actualValueLCL> <planValueBSE>1000</planValueBSE> <planValueLCL>1000</planValueLCL> </cell> <cell> <period> <periodStartDate>2023-11-01</periodStartDate> <periodType>MONTH</periodType> </period> <actualValueBSE>300</actualValueBSE> <actualValueLCL>300</actualValueLCL> <planValueBSE>1000</planValueBSE> <planValueLCL>1000</planValueLCL> </cell> <cell> <period> <periodStartDate>2023-12-01</periodStartDate> <periodType>MONTH</periodType> </period> <actualValueBSE>300</actualValueBSE> <actualValueLCL>300</actualValueLCL> <planValueBSE>1000</planValueBSE> <planValueLCL>1000</planValueLCL> </cell> </cells> <userData/> </line> <line> <expenseType>Operating</expenseType> <laborType>Labor</laborType> <category>Employee</category> <syncSourceCode>NO_SYNC</syncSourceCode> <editable>true</editable> <cells> <cell> <period> <periodStartDate>2023-01-01</periodStartDate> <periodType>MONTH</periodType> </period> <actualValueBSE>300</actualValueBSE> <actualValueLCL>300</actualValueLCL> <planValueBSE>1000</planValueBSE> <planValueLCL>1000</planValueLCL> </cell> <cell> <period> <periodStartDate>2023-02-01</periodStartDate> <periodType>MONTH</periodType> </period> <actualValueBSE>300</actualValueBSE> <actualValueLCL>300</actualValueLCL> <planValueBSE>1000</planValueBSE> <planValueLCL>1000</planValueLCL> </cell> <cell> <period> <periodStartDate>2023-03-01</periodStartDate> <periodType>MONTH</periodType> </period> <actualValueBSE>300</actualValueBSE> <actualValueLCL>300</actualValueLCL> <planValueBSE>1000</planValueBSE> <planValueLCL>1000</planValueLCL> </cell> <cell> <period> <periodStartDate>2023-04-01</periodStartDate> <periodType>MONTH</periodType> </period> <actualValueBSE>300</actualValueBSE> <actualValueLCL>300</actualValueLCL> <planValueBSE>1000</planValueBSE> <planValueLCL>1000</planValueLCL> </cell> <cell> <period> <periodStartDate>2023-05-01</periodStartDate> <periodType>MONTH</periodType> </period> <actualValueBSE>300</actualValueBSE> <actualValueLCL>300</actualValueLCL> <planValueBSE>1000</planValueBSE> <planValueLCL>1000</planValueLCL> </cell> <cell> <period> <periodStartDate>2023-06-01</periodStartDate> <periodType>MONTH</periodType> </period> <actualValueBSE>300</actualValueBSE> <actualValueLCL>300</actualValueLCL> <planValueBSE>1000</planValueBSE> <planValueLCL>1000</planValueLCL> </cell> <cell> <period> <periodStartDate>2023-07-01</periodStartDate> <periodType>MONTH</periodType> </period> <actualValueBSE>300</actualValueBSE> <actualValueLCL>300</actualValueLCL> <planValueBSE>1000</planValueBSE> <planValueLCL>1000</planValueLCL> </cell> <cell> <period> <periodStartDate>2023-08-01</periodStartDate> <periodType>MONTH</periodType> </period> <actualValueBSE>300</actualValueBSE> <actualValueLCL>300</actualValueLCL> <planValueBSE>1000</planValueBSE> <planValueLCL>1000</planValueLCL> </cell> <cell> <period> <periodStartDate>2023-09-01</periodStartDate> <periodType>MONTH</periodType> </period> <actualValueBSE>300</actualValueBSE> <actualValueLCL>300</actualValueLCL> <planValueBSE>1000</planValueBSE> <planValueLCL>1000</planValueLCL> </cell> <cell> <period> <periodStartDate>2023-10-01</periodStartDate> <periodType>MONTH</periodType> </period> <actualValueBSE>300</actualValueBSE> <actualValueLCL>300</actualValueLCL> <planValueBSE>1000</planValueBSE> <planValueLCL>1000</planValueLCL> </cell> <cell> <period> <periodStartDate>2023-11-01</periodStartDate> <periodType>MONTH</periodType> </period> <actualValueBSE>300</actualValueBSE> <actualValueLCL>300</actualValueLCL> <planValueBSE>1000</planValueBSE> <planValueLCL>1000</planValueLCL> </cell> <cell> <period> <periodStartDate>2023-12-01</periodStartDate> <periodType>MONTH</periodType> </period> <actualValueBSE>300</actualValueBSE> <actualValueLCL>300</actualValueLCL> <planValueBSE>1000</planValueBSE> <planValueLCL>1000</planValueLCL> </cell> </cells> <userData/> </line> </lines> <userData/> </forecastActual> <snapshots/> <npv>-24000.0</npv> <tnr>-24000.0</tnr> </service:financialSummary> </service:readFinancialSummaryResponse> </soapenv:Body>')

        code, data = request_in_a_function(r"/Portfolio/portfolio_api.yaml", "create proposal staffing profile",
                                           f"create proposal staffing profile",
                                           kwargs={"ns1:name": proposal_name,
                                                   "ns1:id": proposal_Id,
                                                   "ns1:plannedStartPeriodFullName": startDate,
                                                   "ns1:plannedFinishPeriodFullName": endDate})
        staffingProfileId = SoapParser().get_first_element_body_by_name(data, "staffingProfileId")
        fsId_list.append({"fsId": fsId, "id": proposal_Id, "requestId": proposal_Id})

        proposal_list.append({"name": proposal_name, "id": proposal_Id, "fsid": fsId, "spid": staffingProfileId, "startDate": startDate, "endDate": endDate})

    elif type_need == "project":

        project_name = "ws_project_"+random_str(16)
        startDate = random_choice(month) + ' ' + str(generate_year())
        endDate = random_choice(month) + ' ' + str(generate_year('y+1'))
        code, data = request_in_a_function(r"/Portfolio/portfolio_api.yaml", "create a project by soap",
                                           "create project",
                                           kwargs={
                                               "pm:plannedStartPeriodFullName": startDate,
                                               "pm:projectName": project_name,
                                               "pm:plannedFinishPeriodFullName": endDate,
                                           })
        requestId = SoapParser().get_first_element_body_by_name(data, "requestId")
        projectId = SoapParser().get_first_element_body_by_name(data, "projectId")
        # setattr(GlobalData.local_data.namespace, f"GD_projectId", projectId)
        code, data = request_in_a_function(r"/Portfolio/portfolio_api.yaml", "Get fsId by ppaId",
                                           f"Get fsId",
                                           kwargs={"fm:parentType": "PROJECT".upper(),
                                                   "fm:id": projectId})

        fsId = SoapParser().get_first_element_body_by_name(data, "id")

        # setattr(GlobalData.local_data.namespace, f"GD_projectfsid", fsId)

        code, data = request_in_a_function(r"/Portfolio/portfolio_api.yaml",
                                           "create financial summary forecastActual",
                                           f"create financial summary forecastActual",
                                           new_path=f"/itg/rest2/fs/{fsId}/forecastActual?fiscalYearId={periodId}",
                                           kwargs={"$..cells": cellsData})

        fsId_list.append({"fsId": fsId, "id": projectId, "requestId": requestId})
        # staffing profile
        code, data = request_in_a_function(r"/Portfolio/portfolio_api.yaml", "create project staffing profile",
                                           f"create project staffing profile",
                                           kwargs={"ns1:name": project_name,
                                                   "ns1:id": projectId,
                                                   "ns1:plannedStartPeriodFullName": startDate,
                                                   "ns1:plannedFinishPeriodFullName": endDate})
        staffingProfileId = SoapParser().get_first_element_body_by_name(data, "staffingProfileId")
        print("add profile")

        project_list.append({"name": project_name, "id": projectId, "fsid": fsId, "spid": staffingProfileId, "startDate": startDate, "endDate": endDate})

def add_position_and_fs():
    list_all = project_list + proposal_list
    for item in list_all:
        formatted_end_date = convert_month_to_date(item["endDate"], is_end_time=False)
        formatted_start_date = convert_month_to_date(item["startDate"])
        code, data = request_in_a_function(r"/Portfolio/portfolio_api.yaml", "add position",
                                           "add position",
                                           kwargs={"$..staffingProfile.id": item["spid"],
                                                   "$..forecasts[?(@.type=='FTE')].startDate":formatted_start_date,
                                                   "$..forecasts[?(@.type=='FTE')].finishDate":formatted_end_date})

def add_content(portfolioId, ppa=None):

    code, data = request_in_a_function(r"/Portfolio/portfolio_api.yaml",
                                       "add content through candidate",
                                       f"add content through candidate",
                                       new_path=f"/itg/rest2/portfolios/{str(portfolioId)}/backlogs/candidates",
                                       ppas=[item["fsId"] for item in ppa] if ppa else [])
    logger.debug(f"add [{ppa}] to {portfolioId}")

def add_to_program(programId, ppa=None):

    id_list = [str(item['requestId']) for item in ppa]
    # body = "&".join(f"requestId={request_id}" for request_id in id_list)
    for i in id_list:
        code, data = request_in_a_function(r"/Portfolio/portfolio_api.yaml",
                                           "add ppas to program",
                                           f"add ppas to program",
                                           new_path=f"/itg/rest2/program/{programId}/content/{i}")
        logger.debug(f"add [{ppa}] to {programId}")

def create_role_and_resource():
    name = "ws_rolo_"+random_str(16)
    code, data = request_in_a_function(r"/Portfolio/portfolio_api.yaml", "create role with role name",
                                       f"create role with role name",
                                       kwargs={"ns1:name": name})
    roleId = SoapParser().get_first_element_body_by_name(data, "id")
    setattr(GlobalData.local_data.namespace, f"GD_role_id", roleId)

    # GlobalData.local_data.namespace.GD_role_id = roleId
    code, data = request_in_a_function(r"/Portfolio/portfolio_api.yaml", "create resource pool",
                                       f"create resource pool")
    poolId = SoapParser().get_first_element_body_by_name(data, "id")
    setattr(GlobalData.local_data.namespace, f"GD_pool_id", poolId)
    # GlobalData.local_data.namespace.GD_pool_id = poolId
    # add position


def thread(n):
    threads = []
    for i in range(0, n):  # n 为并发数
        t = threading.Thread(target=call_method, args=("proposal",))
        t1 = threading.Thread(target=call_method, args=("project",))
        # 针对函数创建线程，target为调用的并发函数，args为调用函数的参数，该参数必须为数组，所以这里加了逗号，如果不加就不是数组，运行会报错
        threads.append(t)  # 添加线程到线程组
        threads.append(t1)
    print(threads)

    for t in threads:
        t.start()  # 开启线程
    for t in threads:
        t.join()  # 等待所有线程终止

def get_global_defaultRegion():
    from comm.unit.GlobalVariable import GlobalData
    from comm.unit.apiMethod import get
    response, res = get(headers={}, address=AC[PROJECT_NAME]["host"] + "/itg/rest2/pm/projects/region/default",
                        data=None,
                        downloadName=None, timeout=8, cookies=None, auth=("admin", "admin"))

    GlobalData.local_data.namespace.GD_global_defaultRegion_id = jsonpath.jsonpath(res, "$..id")[0]
    GlobalData.local_data.namespace.GD_global_defaultRegion_name = jsonpath.jsonpath(res, "$..name")[0]


def split_list_randomly(lst, num_parts):
    random.shuffle(lst)  # 随机打乱列表中的元素
    sublist_size = len(lst) // num_parts  # 每个子列表的大小
    remainder = len(lst) % num_parts  # 列表元素不能整除时的余数

    result = []
    start = 0
    for i in range(num_parts):
        sublist = lst[start:start+sublist_size]  # 取出一个子列表
        result.append(sublist)  # 将子列表添加到结果中
        start += sublist_size  # 更新下一个子列表的起始位置

    # 将余数中的元素依次添加到子列表中，保证元素不重复
    for i in range(remainder):
        result[i].append(lst[start+i])

    return result



if __name__ == '__main__':
    get_global_defaultRegion()
    create_role_and_resource()
    # # query period ids
    periodList = Database().query("ppm_fiscal_periods", [{"column": "period_type", "op": "==", "value": "4"},
                                                         {"column": "(TRUNC(start_date)", "op": ">=",
                                                          "value": f"TO_DATE('{generate_year()}-01-01', 'YYYY-MM-DD')"},
                                                         {"column": "(TRUNC(end_date)", "op": ">=",
                                                          "value": f"TO_DATE('{generate_year()}-12-31', 'YYYY-MM-DD')"}],
                                  ["fiscal_period_id"])
    cellsData = [{"periodId": item["fiscal_period_id"], "localPlanValue": 1000, "localActualValue": 2000} for item in
                 periodList]

    # query year period id
    periodId = Database().query("ppm_fiscal_periods", [{"column": "period_type", "op": "==", "value": "6"},
                                                       {"column": "long_name", "op": "==",
                                                        "value": f"{generate_year()}"}],
                                ["fiscal_period_id"])[0]["fiscal_period_id"]

    thread(2)
    batch_create_data()
    # 将ppa随机分配至三个地方
    list_res = split_list_randomly(fsId_list, 3)
    top_portfolioId = getattr(GlobalData.local_data.namespace, "GD_ws_TOP_ADM_id")
    add_content(top_portfolioId, list_res[0])
    sub_portfolioId = getattr(GlobalData.local_data.namespace, "GD_ws_sub_PPM_id")
    add_content(sub_portfolioId, list_res[2])
    programId_tree = getattr(GlobalData.local_data.namespace, "GD_ws_PGM_id")
    add_to_program(programId_tree, list_res[1])

    add_position_and_fs()


