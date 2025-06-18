# -*- coding:utf-8 -*-
# @File    : checkResult.py
# ***************************
import re
import allure
from comm.script.writeLogs import logger
import pytest
from jsonpath import jsonpath
from decimal import Decimal
from comm.unit import readRelevance, replaceRelevance
from hamcrest import *

from comm.unit.apiSend import send_request
from comm.unit.initializePremiseData import init_premise, merge_pre_and_current_params


def check_json(src_data, dst_data):
    """
    Verified json Check whether the formats of json fields are consistent and keywords exist
    :param src_data: checks the content
    :param dst_data: indicates the data returned by the interface
    :return:
    """
    if isinstance(src_data, list):
        for key in src_data:
            res = jsonpath(dst_data, key[1])
            if res:
                if key[0] == "equal_to":
                    with allure.step(f"Check condition：{key} return the result of parameter verification"):
                        allure.attach(name=f"{key[1]} is equal to {key[2]}",
                                      body=f"Expected value：{key[2]}; Actual value：{res[0]}")
                    try:
                        assert_that(str(res[0]), equal_to(str(key[2])))
                    except AssertionError:
                        allure.attach(name=f"{key[1]} is equal to {key[2]}",
                                      body=f"Expected value：{key[2]}; Actual value：{res[0]}")
                        raise Exception(f"The keyword check failed! JsonPath:[{key[1]}]  Result: {res[0]}! = {key[2]}")
                elif key[0] == "contain":
                    with allure.step(f"Check condition：{key} return the result of parameter verification"):
                        allure.attach(name=f"{key[1]} matches results containing {key[2]}", body=f"Expect {key[2]} to contain {res[0]}; Actual value: {res[0]} in {key[2]}")
                    try:
                        assert_that(res[0], contains_string(key[2]))
                    except AssertionError:
                        raise Exception(f"The keyword check failed! JsonPath:[{key[1]}]  Result: {res[0]} does not include {key[2]}")
                elif key[0] == "less_than":
                    with allure.step(f"Check condition：{key} return the result of parameter verification"):
                        allure.attach(name=f"{key[1]} matches less than {key[2]}", body=f"Expect {key[2]} to less than {res[0]}; Actual value: {res[0]} is not less than {key[2]}")
                    try:
                        assert_that(res[0], less_than(int(key[2])))
                    except AssertionError:
                        raise Exception(f"The keyword value size check failed!JsonPath:[{key[1]}]  Result: {res[0]} is not less than {key[2]}")
                elif key[0] == "more_than":
                    with allure.step(f"Check condition：{key} return the result of parameter verification"):
                        allure.attach(name=f"{key[1]} matches more than {key[2]}", body=f"Expect {key[2]} to more than {res[0]}; Actual value: {res[0]} is not more than {key[2]}")
                    try:
                        assert_that(res[0], greater_than(int(key[2])))
                    except AssertionError:
                        raise Exception(f"The keyword value size check failed!JsonPath:[{key[1]}]  Result: {res[0]} is not more than {key[2]}")
                elif key[0] == "less_than_or_equal_to":
                    with allure.step(f"Check condition：{key} return the result of parameter verification"):
                        allure.attach(name=f"{key[1]} matches less than or equal to {key[2]}", body=f"Expect {key[2]} less than or equal to {res[0]}; Actual value: {res[0]} is more than {key[2]}")
                    try:
                        assert_that(res[0], less_than_or_equal_to(int(key[2])))
                    except AssertionError:
                        raise Exception(f"The keyword value size check failed!JsonPath:[{key[1]}]  Result: {res[0]} is more than {key[2]}")
                elif key[0] == "greater_than_or_equal_to":
                    with allure.step(f"Check condition：{key} return the result of parameter verification"):
                        allure.attach(name=f"{key[1]} match result is greater than or equal to {key[2]}", body=f"Expect：{key[2]};Actual value：{res[0]}")
                    try:
                        assert_that(res[0], greater_than_or_equal_to(int(key[2])))
                    except AssertionError:
                        raise Exception(f"The keyword value size check failed!JsonPath:[{key[1]}]  Result: {res[0]} is less than {key[2]}")
                elif key[0] == "not_equal_to":
                    with allure.step(f"Check condition：{key} return the result of parameter verification"):
                        allure.attach(name=f"{key[1]} does not match {key[2]}", body=f"Expect：{key[2]};Actual value：{res[0]}")
                    try:
                        assert_that(str(res[0]), is_not(equal_to(str(key[2]))))
                    except AssertionError:
                        raise Exception(f"The keyword value size check failed!JsonPath:[{key[1]}]  Result: {res[0]} is equal to {key[2]}")
                elif key[0] == "is_none":
                    with allure.step(f"Check condition：{key} return the result of parameter verification"):
                        allure.attach(name=f"The result of {key[1]} is null", body=f"Expect：is null; Actual value：{res[0]}")
                    try:
                        assert_that(res[0], none())
                    except AssertionError:
                        raise Exception(f"The keyword check failed! JsonPath:[{key[1]}]  Result: {res[0]} is not null")
                elif key[0] == "not_none":
                    with allure.step(f"Check condition：{key} return the result of parameter verification"):
                        allure.attach(name=f"The result of {key[1]} is not null", body=f"Expect：is not null;Actual value：{res[0]}")
                    try:
                        assert_that(res[0], not_none())
                    except AssertionError:
                        raise Exception("The keyword check failed! JsonPath:[{key[1]}]  Result: {res[0]} is null")
                elif key[0] == "=":
                    with allure.step(f"Check condition：{key} returns the result of parameter length check"):
                        allure.attach(name=f"The matching length of {key[1]} is equal to {key[2]}", body=f"Expect：{key[2]};Actual value：{len(res[0])}")
                    try:
                        assert_that(res[0], has_length(key[2]))
                    except AssertionError:
                        raise Exception(f"The keyword length check fails!JsonPath:[{key[1]}] Result: The resulting value of length {len(res[0])} is not equal to the expected length {key[2]}")
                elif key[0] == "<":
                    with allure.step(f"Check condition：{key} Returns the result of parameter length check"):
                        allure.attach(name=f"The matching length of {key[1]} is less than {key[2]}", body=f"Expect：{key[2]};Actual value：{len(res[0])}")
                    try:
                        assert_that(len(res[0]), less_than(key[2]))
                    except AssertionError:
                        raise Exception(f"The keyword length check fails!JsonPath:[{key[1]}] Result: The resulting value of length {len(res[0])} is not less than the expected length {key[2]}")
                elif key[0] == ">":
                    with allure.step(f"Check condition：{key} Returns the result of parameter length check"):
                        allure.attach(name=f"The matching length of {key[1]} is more than {key[2]}", body=f"Expect：{key[2]};Actual value：{len(res[0])}")
                    try:
                        assert_that(len(res[0]), greater_than(key[2]))
                    except AssertionError:
                        raise Exception(f"The keyword length check fails!JsonPath:[{key[1]}] Result: The resulting value of length {len(res[0])} is not more than the expected length {key[2]}")
                elif key[0] == ">=":
                    with allure.step(f"Check condition：{key} Returns the result of parameter length check"):
                        allure.attach(name=f"The matching length of {key[1]} is greater than or equal to{key[2]}", body=f"Expect：{key[2]};Actual value：{len(res[0])}")
                    try:
                        assert_that(len(res[0]), greater_than_or_equal_to(key[2]))
                    except AssertionError:
                        raise Exception(f"The keyword length check fails!JsonPath:[{key[1]}] Result: The resulting value of length {len(res[0])} is less than the expected length {key[2]}")
                elif key[0] == "<=":
                    with allure.step(f"Check condition：{key} Returns the result of parameter length check"):
                        allure.attach(name=f"The matching length of {key[1]} is less than or equal to{key[2]}", body=f"Expect：{key[2]};Actual value：{len(res[0])}")
                    try:
                        assert_that(len(res[0]), less_than_or_equal_to(key[2]))
                    except AssertionError:
                        raise Exception(f"The keyword length check fails!JsonPath:[{key[1]}] Result: The resulting value of length {len(res[0])} is more than the expected length {key[2]}")
                elif key[0] == "!=":
                    with allure.step(f"Check condition：{key} Returns the result of parameter length check"):
                        allure.attach(name=f"The matching length of {key[1]} is not equal to{key[2]}", body=f"Expect：{key[2]};Actual value：{len(res[0])}")
                    try:
                        assert_that(len(res[0]), is_not(equal_to(key[2])))
                    except AssertionError:
                        raise Exception(f"The keyword length check fails!JsonPath:[{key[1]}] Result: The resulting value of length {len(res[0])} is equal to the expected length {key[2]}")
            else:
                raise Exception("JSON format check, keyword %s is not returned %s!" % (key, dst_data))

    else:
        raise Exception("JSON verifies that the content is not in list format：{}".format(src_data))


def check_database(actual, expected, mark=''):
    """
    Check database
    :param actual: actual result
    :param expected: param expected
    :param mark: indicates the identifier
    :return:
    """
    if isinstance(actual, dict) and isinstance(expected, dict):
        result = list()
        logger.info('Check database {}>>>'.format(mark))
        content = '\n%(key)-20s%(actual)-40s%(expected)-40s%(result)-10s' \
                % {'key': 'KEY', 'actual': 'ACTUAL', 'expected': 'EXPECTED', 'result': 'RESULT'}
        for key in expected:
            if key in actual:
                actual_value = actual[key]
            else:
                actual_value = None
            expected_value = expected[key]
            if actual_value or expected_value:
                if isinstance(actual_value, (int, float, Decimal)):
                    if int(actual_value) == int(expected_value):
                        rst = 'PASS'
                    else:
                        rst = 'FAIL'
                else:
                    if str(actual_value) == str(expected_value):
                        rst = 'PASS'
                    else:
                        rst = 'FAIL'
            else:
                rst = 'PASS'
            result.append(rst)
            line = '%(key)-20s%(actual)-40s%(expected)-40s%(result)-10s' \
                % {'key': key, 'actual': str(actual_value) + ' ',
                            'expected': str(expected_value) + ' ', 'result': rst}
            content = content + '\n' + line
        logger.info(content)
        allure.attach(name="Check database details {}".format(mark[-1]), body=str(content))
        if 'FAIL' in result:
            raise AssertionError('Check database {} failed!'.format(mark))

    elif isinstance(actual, list) and isinstance(expected, list):
        result = list()
        logger.info('Check database {}>>>'.format(mark))
        content = '\n%(key)-25s%(actual)-35s%(expected)-35s%(result)-10s' \
                % {'key': 'INDEX', 'actual': 'ACTUAL', 'expected': 'EXPECTED', 'result': 'RESULT'}
        for index in range(len(expected)):
            if index < len(actual):
                actual_value = actual[index]
            else:
                actual_value = None
            expected_value = expected[index]
            if actual_value or expected_value:
                if isinstance(actual_value, (int, float, Decimal)):
                    if int(actual_value) == int(expected_value):
                        rst = 'PASS'
                    else:
                        rst = 'FAIL'
                else:
                    if str(actual_value) == str(expected_value):
                        rst = 'PASS'
                    else:
                        rst = 'FAIL'
            else:
                rst = 'PASS'
            result.append(rst)
            line = '%(key)-25s%(actual)-35s%(expected)-35s%(result)-10s' \
                % {'key': index, 'actual': str(actual_value) + ' ',
                            'expected': str(expected_value) + ' ', 'result': rst}
            content = content + '\n' + line
        logger.info(content)
        allure.attach(name="Check database detail {}".format(mark[-1]), body=str(content))
        if 'FAIL' in result:
            raise AssertionError('Check database {} failed!'.format(mark))

    else:
        logger.info('Check database {}>>>'.format(mark))
        logger.info('ACTUAL: {}\nEXPECTED: {}'.format(actual, expected))
        if str(expected) != str(actual):
            raise AssertionError('Check database {} failed!'.format(mark))


def check_by_request(case_info, case_data, data, relevance):
    if case_data.get("validate", None):
        for item in case_data.get("validate"):
            # allure.attach()
            case_info["address"] = item["url"]
            case_info["mime_type"] = item["mime_type"]
            case_info["method"] = item["method"]
            case_data["address"] = item["url"]
            case_data["parameter"] = item["body"]
            case_info["setup"] = None
            case_data["premise"] = None
            case_data["setup_function"] = None
            with allure.step("Check by other api"):
                test_info, case_data, relevance = init_premise(case_info, case_data, "", relevance)
                res, res_data = send_request(test_info, case_data)
                check_result(item, res.status_code, res_data)


def check_result(case_data, code, data):
    """
    Verification test result
    :param case_data: use case data
    :param code: indicates the interface status code
    :param data: Returned json data of the interface
    :return:
    """
    try:
        check_type = case_data['check_body']['check_type']
        expected_code = case_data['check_body']['expected_code']
        expected_result = case_data['check_body']['expected_result']
    except Exception as e:
        raise KeyError('Failed to obtain use case check information：{}'.format(e))

    if check_type == 'no_check':
        with allure.step("The interface result is not verified"):
            pass

    elif check_type == 'check_code':
        with allure.step("Only the interface status code is verified"):
            allure.attach(name="Actual code", body=str(code))
            allure.attach(name="Expected code", body=str(expected_code))
            allure.attach(name='Actual data', body=str(data))
        if int(code) != expected_code:
            raise Exception("status code is incorrect!\n %s != %s" % (code, expected_code))

    elif check_type == 'check_json':
        with allure.step("JSON format and parameter verification interface"):
            allure.attach(name="Actual code", body=str(code))
            allure.attach(name="Expected code", body=str(expected_code))
            allure.attach(name='Actual data', body=str(data))
            allure.attach(name='Expected data', body=str(expected_result))
        # assert_that(int(expected_code), equal_to(int(code)))
        if int(code) == expected_code:
            if not data:
                data = "{}"
            check_json(expected_result, data)
        else:

            logger.exception(Exception("status code is incorrect!\n %s != %s" % (code, expected_code)))
            raise Exception("status code is incorrect!\n %s != %s" % (code, expected_code))

    elif check_type == 'entirely_check':
        with allure.step("Complete check interface result"):
            allure.attach(name="Actual code", body=str(code))
            allure.attach(name="Expected code", body=str(expected_code))
            allure.attach(name='Actual data', body=str(data))
            allure.attach(name='Expected data', body=str(expected_result))
        if int(code) == expected_code:
            try:
                assert_that(expected_result, equal_to(data))
            except AssertionError:
                raise Exception("Complete check failure! %s ! = %s" % (expected_result, data))
        else:
            raise Exception("status code is incorrect!\n %s != %s" % (code, expected_code))

    elif check_type == 'regular_check':
        if int(code) == expected_code:
            try:
                result = ""
                if isinstance(expected_result, list):
                    for i in expected_result:
                        result = re.findall(i.replace("\"", "\""), str(data))
                        allure.attach('Check completion result\n', str(result))
                else:
                    result = re.findall(expected_result.replace("\"", "\'"), str(data))
                    with allure.step("Regular check interface result"):
                        allure.attach(name="Actual code", body=str(code))
                        allure.attach(name="Expected code", body=str(expected_code))
                        allure.attach(name='Actual data', body=str(data))
                        allure.attach(name='Expected data', body=str(expected_result).replace("\'", "\""))
                        allure.attach(name=expected_result.replace("\"", "\'") + 'Check completion result',
                                      body=str(result).replace("\'", "\""))
                if not result:
                    raise Exception("The content is not checked by the RE! %s" % expected_result)
            except KeyError:
                raise Exception("The regular check failed! %s\n the regular expression is null" % expected_result)
        else:
            raise Exception("status code is incorrect!\n %s != %s" % (code, expected_code))

    else:
        raise Exception("None Check mode of the interface%s" % check_type)

    if 'check_db' in case_data:
        from comm.unit import queryDatabase as qdb
        check_db = case_data['check_db']
        data['parameter'] = case_data['parameter']
        __relevance = readRelevance.get_relevance(data, check_db)
        check_db = replaceRelevance.replace(check_db, __relevance)

        for each in check_db:
            try:
                check_type = each['check_type']
                execute_sql = each['execute_sql']
                expected_result = each['expected_result']
            except KeyError as e:
                raise KeyError('[check_db] has an error field!\n{}'.format(e))
            except TypeError:
                raise KeyError("The [check_db] type is incorrect,Expected <class 'list'>, not %s!" % type(expected_result))
            if not isinstance(expected_result, list):
                raise KeyError("The [expected_result] type is incorrect, Expected <class 'list'>, not %s!" % type(expected_result))

            exp = r"^select (.*?) from (.*?) where (.*?)$"
            res = re.findall(exp, execute_sql.strip().lower())[0]
            for r in res:
                if not each:
                    msg = 'Standard format: ' + exp
                    raise Exception('Invalid SQL>>> {}\n{}'.format(execute_sql, msg))
            actual = qdb.QueryDB.main_query(execute_sql)

            mark = check_type.replace('check_', '').upper() + '['+res[1]+']'
            with allure.step("Check database {}".format(mark)):
                allure.attach(name="Actual result", body=str(actual))
                allure.attach(name='Expected result', body=str(expected_result))
                if "expected_num" in each.keys():
                    expected_num = each['expected_num']
                    allure.attach(name="Actual number of lines", body=str(len(actual)))
                    allure.attach(name='Expected number of lines', body=str(expected_num))
                    if len(actual) != int(expected_num):
                        raise AssertionError('Check database {} row number failed!'.format(mark))
                for index, expected in enumerate(expected_result):
                    try:
                        check_database(actual[index], expected, mark+str(index))
                    except IndexError:
                        raise IndexError('Failed to verify database {}; Expected result exceeded Actual entry!'.format(mark+str(index)))
