
# @File    : apiSend.py
# ***********************
import json
from comm.script.writeLogs import logger
import allure
import time
from config import INTERVAL, PROXY, PROXIES
from comm.unit import apiMethod


def send_request(test_info, case_data, CallFunctionDes=None):
    """
    Encapsulation request
    :param test_info: test information
    :param case_data: use case data
    :param CallFunctionDes: current behavior description
    :return:
    """
    try:
        address = case_data.get("address", False)
        host = test_info["host"]
        method = case_data["method"].upper() if case_data.get("method", False) else test_info["method"].upper()
        address = case_data["address"] if address else test_info["address"]
        mime_type = case_data["mime_type"] if case_data.get("mime_type", False) else test_info["mime_type"]
        headers = test_info["headers"]
        cookies = test_info["cookies"]
        file = test_info["file"]
        timeout = test_info["timeout"]
        summary = case_data["summary"]
        parameter = case_data["parameter"]
        auth = tuple(case_data["auth"]) if case_data["auth"] else tuple(test_info["auth"])
        download_name = case_data["download_name"] if 'download_name' in case_data.keys() else None
        if PROXY:
            proxies = PROXIES
    except Exception as e:
        raise KeyError(f'Failed to obtain basic information about the case:{e}')

    request_url = host + address
    logger.info("=" * 150)
    logger.info(f"Host：{str(host)}")
    logger.info(f"Path：{str(address)}")
    logger.info(f"Headers: {str(headers)}")
    logger.info(f"Parameters: {str(parameter)}")
    step = CallFunctionDes if CallFunctionDes else case_data['summary']

    if summary == 'save_cookies':
        with allure.step("Save cookies"):
            allure.attach(name="Host", body=str(host))
            allure.attach(name="Path", body=str(address))
            allure.attach(name="Headers", body=str(headers))
            allure.attach(name="Parameters", body=str(parameter))
            apiMethod.save_cookie(headers=headers,
                                  address=request_url,
                                  mime_type=mime_type,
                                  data=parameter,
                                  cookies=cookies,
                                  timeout=timeout)
    if method == 'POST':
        logger.info("Request method: POST")
        if file:
            result = apiMethod.post(headers=headers,
                                    address=request_url,
                                    mime_type=mime_type,
                                    files=case_data["file"],
                                    data=parameter,
                                    auth=auth,
                                    cookies=cookies,
                                    proxy=proxies,
                                    timeout=timeout)
            with allure.step(f"POST upload file[{step}]"):
                allure.attach(name="Host", body=str(host))
                allure.attach(name="Path", body=str(address))
                allure.attach(name="Headers", body=str(result[0].request.headers))
                allure.attach(name="Parameters", body=str(parameter))
                allure.attach(name="Uploaded file", body=str(case_data["file"]))
                allure.attach(name="Response headers", body=str(result[0].headers))
                allure.attach(name="Response", body=str(f"status_code:{result[0]}"+" result:"+result[1]))
        else:
            result = apiMethod.post(headers=headers,
                                    address=request_url,
                                    mime_type=mime_type,
                                    data=parameter,
                                    auth=auth,
                                    proxy=proxies,
                                    cookies=cookies,
                                    timeout=timeout)
            with allure.step(f"POST [{step}]"):
                allure.attach(name="Host", body=str(host))
                allure.attach(name="Path", body=str(address))
                allure.attach(name="Headers", body=str(result[0].request.headers))
                allure.attach(name="Parameters", body=str(parameter))
                allure.attach(name="Response headers", body=str(result[0].headers))
                allure.attach(name="Response", body=f"status_code:{result[0].status_code} result: "+str(result[1]))
            logger.info("Request result: %s" % str(result))
    elif method == 'GET':
        logger.info("Request method: GET")
        result = apiMethod.get(headers=headers,
                               address=request_url,
                               data=parameter,
                               cookies=cookies,
                               auth=auth,
                               proxy=proxies,
                               timeout=timeout,
                               downloadName=download_name)

        with allure.step(f"GET [{step}]"):
            allure.attach(name="Host", body=str(host))
            allure.attach(name="Path", body=str(address))
            allure.attach(name="Headers", body=str(result[0].request.headers))
            allure.attach(name="Parameters", body=str(parameter))
            allure.attach(name="Response headers", body=str(result[0].headers))
            allure.attach(name="Response", body=f"status_code:{result[0].status_code} result: " + str(result[1]))

    elif method == 'PUT':
        logger.info("Request method: PUT")
        if file:
            result = apiMethod.put(headers=headers,
                                   address=request_url,
                                   mime_type=mime_type,
                                   files=parameter,
                                   auth=auth,
                                   proxy=proxies,
                                   cookies=cookies,
                                   timeout=timeout)
            with allure.step(f"PUT uploaded file[{step}]"):
                allure.attach(name="Host", body=str(host))
                allure.attach(name="Path", body=str(address))
                allure.attach(name="Headers", body=str(result[0].request.headers))
                allure.attach(name="Uploaded file", body=str(case_data["file"]))
                allure.attach(name="Parameters", body=str(parameter))
                allure.attach(name="Response headers", body=str(result[0].headers))
                allure.attach(name="Response", body=f"status_code:{result[0].status_code} result: " + str(result[1]))

        else:
            result = apiMethod.put(headers=headers,
                                   address=request_url,
                                   mime_type=mime_type,
                                   data=parameter,
                                   auth=auth,
                                   proxy=proxies,
                                   cookies=cookies,
                                   timeout=timeout)
            with allure.step(f"PUT [{step}]"):
                allure.attach(name="Host", body=str(host))
                allure.attach(name="Path", body=str(address))
                allure.attach(name="Headers", body=str(result[0].request.headers))
                allure.attach(name="Parameters", body=str(parameter))
                allure.attach(name="Response headers", body=str(result[0].headers))
                allure.attach(name="Response", body=f"status_code:{result[0].status_code} result: " + str(result[1]))
    elif method == 'DELETE':
        logger.info("Request method: DELETE")
        result = apiMethod.delete(headers=headers,
                                  address=request_url,
                                  data=parameter,
                                  auth=auth,
                                  proxy=proxies,
                                  cookies=cookies,
                                  timeout=timeout)
        with allure.step(f"DELETE [{step}]"):
            allure.attach(name="Host", body=str(host))
            allure.attach(name="Path", body=str(address))
            allure.attach(name="Headers", body=str(result[0].request.headers))
            allure.attach(name="Parameters", body=str(parameter))
            allure.attach(name="Response headers", body=str(result[0].headers))
            allure.attach(name="Response", body=f"status_code:{result[0].status_code} result: " + str(result[1]))
    else:
        result = {"code": None, "data": None}
    logger.info("Request result: %s" % str(result))
    time.sleep(INTERVAL)
    return result
