# -*- coding:utf-8 -*-
# @File    : apiMethod.py
# *************************
import os
import json
import random
from comm.script.writeLogs import logger
import xmltodict
from contextlib import closing
import mimetypes
import time
import allure
import requests
import simplejson
from requests_toolbelt import MultipartEncoder
from comm.utils.readYaml import write_yaml_file, read_yaml_data
from config import API_CONFIG, PROJECT_NAME, UPLOAD_DIR, DOWNLOAD_DIR


def post(headers, address, mime_type, timeout=120, data=None, files=None, cookies=None, auth=None, proxy=None):
    """
    post request
    :param headers: request head
    :param address: request address
    :param mime_type: request parameter format (form_data,raw)
    :param timeout: indicates the timeout period
    :param data: request parameter
    :param files: file path
    :param cookies:
    :return:
    """
    headers["Accept"] = "application/json"
    # 判断请求参数类型
    if 'form-data' in mime_type:
        response = None
        if files:
            if isinstance(files, str):
                if files == '_':
                    enc = None
                else:
                    param_key = files.split(' ')[0]
                    filename = files.split(' ')[1]
                    value = UPLOAD_DIR + filename
                    path_l = {"{}".format(param_key): (os.path.basename(value), open(value, 'rb'))}
                    enc = MultipartEncoder(
                        fields=path_l,
                        boundary='--------------' + str(random.randint(1e28, 1e29 - 1))
                    )
                    headers['Content-Type'] = enc.content_type
                response = requests.post(url=address,
                                         data=enc,
                                         params=data,
                                         headers=headers,
                                         auth=auth,
                                         timeout=int(timeout),
                                         proxies=proxy,
                                         cookies=cookies)
            elif isinstance(files, list):
                datas = []
                for item in files:
                    param, filename = item.split(' ')
                    types_ = mimetypes.guess_type(filename)[0]
                    d = (param, (filename, open(UPLOAD_DIR + filename, 'rb'), types_))
                    datas.append(d)
                response = requests.post(url=address, headers=headers, data=data, files=datas,
                                         cookies=cookies, timeout=120)
            else:
                logger.debug("The file format is not supported!")
        else:
            datas = None
            response = requests.post(url=address, headers=headers, data=data, files=datas,
                                     cookies=cookies, timeout=120)
    elif 'data' in mime_type or 'x-www-form-urlencoded' in mime_type:
        start_time = time.time()
        response = requests.post(url=address,
                                 data=data,
                                 headers=headers,
                                 timeout=int(timeout),
                                 files=files,
                                 auth=auth,
                                 cookies=cookies)
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"Request time：{elapsed_time}seconds")
    elif 'xml' in mime_type or 'application/xml' in mime_type:
        headers['Content-Type'] = "text/xml"
        headers["Accept"] = "text/xml"
        start_time = time.time()
        response = requests.post(url=address,
                                 data=data,
                                 headers=headers,
                                 timeout=int(timeout),
                                 files=files,
                                 auth=auth,
                                 cookies=cookies)
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"Request time：{elapsed_time}seconds")
    else:
        start_time = time.time()
        response = requests.post(url=address,
                                 json=data,
                                 headers=headers,
                                 timeout=int(timeout),
                                 auth=auth,
                                 files=files,
                                 cookies=cookies)
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"Request time：{elapsed_time}seconds")
    try:
        if response.headers.get('Content-Type', False):
            if response.headers.get('Content-Type', False) == "application/json":
                return response, response.json()
            else:
                return response, response.content
        else:
            return response, response.content
    except json.decoder.JSONDecodeError:
        return response, None
    except simplejson.errors.JSONDecodeError:
        return response, None
    except Exception as e:
        logger.exception('ERROR')
        logger.error(e)
        raise


def get(headers, address, data, downloadName=None, timeout=8, cookies=None, auth=None, proxy=None):
    """
    get request
    :param headers: request head
    :param address: request address
    :param data: request parameter
    :param timeout: indicates the timeout period
    :param downloadName: specifies the name of the download file
    :param cookies:
    :param auth:
    :return:
    """
    headers["Accept"] = "application/json"
    start_time = time.time()
    response = requests.get(url=address,
                            params=data,
                            headers=headers,
                            timeout=int(timeout),
                            auth=auth,
                            cookies=cookies,
                            proxies=proxy,
                            verify=False)
    end_time = time.time()
    elapsed_time = end_time - start_time
    logger.info(f"Request time：{elapsed_time}seconds")
    if response.status_code == 301:
        response = requests.get(url=response.headers["location"])
    try:
        if downloadName:
            if response.status_code == 200:
                file = download_file(response, downloadName)
                EXT = os.path.splitext(file)[1]
                fileN = os.path.basename(os.path.splitext(file)[0] + EXT)
                with open(file, "rb") as f:
                    context = f.read()
                    allure.attach(context, fileN, attachment_type=eval('allure.attachment_type.{}'
                                                                       .format(EXT.strip('.').upper())))
        return response, response.json() if response.headers["Content-Type"] == "application/json" else xmltodict.parse(
            response.content)
    except json.decoder.JSONDecodeError:
        return response, response.text
    except simplejson.errors.JSONDecodeError:
        return response, response.text
    except Exception as e:
        logger.exception('ERROR')
        logger.error(e)
        raise


def put(headers, address, mime_type, timeout=8, data=None, files=None, cookies=None, auth=None, proxy=None):
    """
    put request
    :param headers: request head
    :param address: request address
    :param mime_type: request parameter format (form_data,raw)
    :param timeout: indicates the timeout period
    :param data: request parameter
    :param files: file path
    :param cookies:
    :return:
    """
    headers["Accept"] = "application/json"
    if mime_type == 'raw':
        data = json.dumps(data)
    elif mime_type == 'application/json':
        headers['Content-Type'] = "application/json"
        data = json.dumps(data)
    start_time = time.time()
    response = requests.put(url=address,
                            data=data,
                            headers=headers,
                            timeout=int(timeout),
                            files=files,
                            auth=auth,
                            cookies=cookies,
                            proxies=proxy,
                            verify=False)
    end_time = time.time()
    elapsed_time = end_time - start_time
    logger.info(f"Request time：{elapsed_time}seconds")
    try:
        return response, response.json() if response.headers["Content-Type"] == "application/json" else xmltodict.parse(
            response.content)
    except json.decoder.JSONDecodeError:
        return response, None
    except simplejson.errors.JSONDecodeError:
        return response, None
    except Exception as e:
        logger.exception('ERROR')
        logger.error(e)
        raise


def delete(headers, address, data, timeout=8, cookies=None, auth=None, proxy=None):
    """
    delete request
    :param headers: request head
    :param address: request address
    :param data: request parameter
    :param timeout: indicates the timeout period
    :param cookies:
    :return:
    """
    headers["Accept"] = "application/json"
    start_time = time.time()
    response = requests.delete(url=address,
                               params=data,
                               headers=headers,
                               timeout=int(timeout),
                               cookies=cookies,
                               auth=auth,
                               proxies=proxy,
                               verify=False)
    end_time = time.time()
    elapsed_time = end_time - start_time
    logger.info(f"Request time：{elapsed_time}seconds")
    try:
        return response, response.json() if response.headers["Content-Type"] == "application/json" else xmltodict.parse(
            response.content)
    except json.decoder.JSONDecodeError:
        return response, None
    except simplejson.errors.JSONDecodeError:
        return response, None
    except Exception as e:
        logger.exception('ERROR')
        logger.error(e)
        raise


def save_cookie(headers, address, mime_type, timeout=8, data=None, files=None, cookies=None, auth=None, proxy=None):
    """
    Save cookie information
    :param headers: request head
    :param address: request address
    :param mime_type: request parameter format (form_data,raw)
    :param timeout: indicates the timeout period
    :param data: request parameter
    :param files: file path
    :param cookies:
    :return:
    """
    headers["Accept"] = "application/json"
    if 'data' in mime_type:
        response = requests.post(url=address,
                                 data=data,
                                 headers=headers,
                                 timeout=int(timeout),
                                 files=files,
                                 auth=auth,
                                 proxies=proxy,
                                 cookies=cookies,
                                 verify=False)
    else:
        response = requests.post(url=address,
                                 json=data,
                                 headers=headers,
                                 timeout=timeout,
                                 files=files,
                                 cookies=cookies,
                                 verify=False)
    try:
        cookies = response.cookies.get_dict()
        aconfig = read_yaml_data(API_CONFIG)
        aconfig[PROJECT_NAME]['cookies'] = cookies
        write_yaml_file(API_CONFIG, aconfig)
        logger.debug("The cookies have been saved and the result is:{}".format(cookies))
    except json.decoder.JSONDecodeError:
        return response, None
    except simplejson.errors.JSONDecodeError:
        return response, None
    except Exception as e:
        logger.exception('ERROR')
        logger.error(e)
        raise


def download_file(res, filename):
    """
    Save the file data downloaded after the request interface
    :param res: Returned data of the download interface
    :param filename: Download filename (including extension name)
    :return: path to the saved file
    """
    fileName = DOWNLOAD_DIR + filename
    import os
    if os.path.exists(fileName):
        os.remove(fileName)
    with closing(res) as response:
        with open(fileName, 'wb') as fd:
            for chunk in response.iter_content(128):
                fd.write(chunk)
    return fileName


if __name__ == '__main__':
    pass
