#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @author： 刘宣妤
# @file： initializeFunc.py
# datetime： 2021/7/19 9:57 
# ide： PyCharm
import hashlib
from comm.unit.apiMethod import *
# from comm.unit.queryDatabase import QueryDB
from config import PROJECT_NAME, AC


def func_header():
    """
    更新open接口header
    """
    SECRET = AC[PROJECT_NAME]['app_secret']
    TOKEN = AC[PROJECT_NAME]['app_token']
    timestamp = str(round(time.time() * 1000))
    signature = TOKEN.strip() + SECRET.strip() + timestamp.strip()
    md5 = hashlib.md5(signature.encode(encoding='utf-8')).hexdigest()
    header = {
        'x-qys-accesstoken': TOKEN,
        'x-qys-timestamp': timestamp,
        'x-qys-signature': md5
    }
    return header


def func_DoSql(sql, count=1, db=None):
    if 'select' in sql or 'SELECT' in sql:
        res_data = QueryDB().main_query(sql, count=count, db=db)
        if res_data:
            if len(res_data[0]) == 1:
                for k, v in res_data[0].items():
                    return v
            else:
                return res_data[0]
    else:
        QueryDB().main_excute(sql)


if __name__ == '__main__':
    c = func_header()
    print(c)

