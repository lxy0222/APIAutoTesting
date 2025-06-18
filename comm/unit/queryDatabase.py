# -*- coding:utf-8 -*-
# @Time    : 2021/07/10
# @Author  : Xuanyu Liu
# @File    : queryDatabase.py
# **************************
import pymssql

from comm.utils.readYaml import read_yaml_data
from config import DB_CONFIG, PROJECT_NAME, DB_TYPE, AC
from comm.script.writeLogs import logger
import time
import re
import pandas as pd

dbcfg = read_yaml_data(DB_CONFIG)[PROJECT_NAME]

import pymysql
import cx_Oracle
import pyodbc
import psycopg2
import psycopg2.extras


class DBUtils:
    def __init__(self):
        self.db_type = DB_TYPE
        self.db_host = dbcfg['host']
        self.db_port = dbcfg['port']
        self.db_user = dbcfg['user']
        self.db_password = dbcfg['password']
        self.db_name = dbcfg['database']
        self.conn = None
        self.cursor = None

    def connect(self):
        if self.db_type == 'mysql':
            self.conn = pymysql.connect(
                host=self.db_host,
                port=self.db_port,
                user=self.db_user,
                password=self.db_password,
                database=self.db_name,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
        elif self.db_type == 'oracle':
            dsn_tns = cx_Oracle.makedsn(self.db_host, self.db_port, service_name=self.db_name)
            self.conn = cx_Oracle.connect(
                user=self.db_user,
                password=self.db_password,
                dsn=dsn_tns,
                encoding='UTF-8'
            )
        elif self.db_type == 'sqlserver':
            driver = '{SQL Server}'
            server = '{}:{}'.format(self.db_host, self.db_port)
            database = self.db_name
            uid = self.db_user
            pwd = self.db_password
            self.conn = pyodbc.connect(
                'DRIVER={};SERVER={};DATABASE={};UID={};PWD={}'.format(driver, server, database, uid, pwd)
            )
        elif self.db_type == 'postgresql':
            try:
                self.conn = psycopg2.connect(database=self.db_name,
                                             user=self.db_user,
                                             password=self.db_password,
                                             host=self.db_host,
                                             cursor_factory=psycopg2.extras.DictCursor,
                                             port=str(self.db_port))
            except psycopg2.Error as e:
                print(e)
        self.cursor = self.conn.cursor()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def execute(self, sql, params=None):
        self.cursor.execute(sql, params)
        self.conn.commit()

    def fetch_one(self, sql, params=None):

        self.cursor.execute(sql, params)
        data = pd.read_sql(sql, con=self.conn)
        result = self.cursor.fetchone()
        return data

    def fetch_all(self, sql, params=None):
        self.cursor.execute(sql, params)
        data = pd.read_sql(sql, con=self.conn)
        result = self.cursor.fetchall()
        return data


if __name__ == '__main__':
    db = DBUtils()
    db.connect()
    print(db.fetch_one("select * from kcrt_fg_pfm_proposal where request_id = 30122"))
