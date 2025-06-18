#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @author： 刘宣妤
# @file： pushDing.py
# datetime： 2021/8/25 17:35 
# ide： PyCharm

import os
import jenkins
import requests
import json
import yaml


def read_yaml_data(yaml_file):
    yaml_file = yaml_file.replace('\\', '/')
    with open(yaml_file, 'r', encoding="utf-8") as fr:
        return yaml.load(fr, Loader=yaml.SafeLoader)


ROOT_DIR = str(os.path.realpath(__file__)).split('report')[0].replace('\\', '/')
RUN_CONFIG = ROOT_DIR+'config/runConfig.yml'
RC = read_yaml_data(RUN_CONFIG)
REPORT_DIR = ROOT_DIR + 'report'


# jenkins连接信息
jenkins_conf = RC["Jenkins_conf"]
# 获取jenkins对象
server = jenkins.Jenkins(**jenkins_conf)  # Jenkins登录名 ，密码
# job名称
job_name = RC["job_name"]  # Jenkins运行任务名称
# job的url地址
job_url = jenkins_conf["url"] + job_name
# 获取最后一次构建
job_last_build_url = server.get_info(job_name)['lastBuild']['url']
# 报告地址
report_url = job_last_build_url + 'allure'  # 'allure'为我的Jenkins全局工具配置中allure别名

'''
钉钉推送方法：
读取report文件中"prometheusData.txt"，循环遍历获取需要的值。
使用钉钉机器人的接口，拼接后推送text
'''


def DingTalkSend():
    d = {}
    # 打开prometheusData 获取需要发送的信息
    f = open(REPORT_DIR + '/html/export/prometheusData.txt', 'r')

    for lines in f:
        for c in lines:
            launch_name = lines.strip('\n').split(' ')[0]
            num = lines.strip('\n').split(' ')[1]
            d.update({launch_name: num})
    print(d)
    f.close()
    retries_run = d.get('launch_retries_run')  # 运行总数
    print('运行总数:{}'.format(retries_run))
    status_passed = d.get('launch_status_passed')  # 通过数量
    print('通过数量：{}'.format(status_passed))
    status_failed = str(int(retries_run) - int(status_passed))  # 不通过数量
    print('失败数量：{}'.format(status_failed))

    # 钉钉推送

    url = RC["dd_url"]  # webhook
    con = {"msgtype": "text",
           "text": {
               "content": "==========接口自动化测试脚本执行完成=========="
                          "\n测试概述:"
                          "\n运行总数:" + retries_run +
                          "\n通过数量:" + status_passed +
                          "\n失败数量:" + status_failed +
                          "\n构建地址：\n" + job_url +
                          "\n报告地址：\n" + report_url
           }
           }
    res = requests.post(url, data=json.dumps(con), headers={'Content-Type': 'application/json'})
    print(res.json())


if __name__ == '__main__':
    DingTalkSend()
