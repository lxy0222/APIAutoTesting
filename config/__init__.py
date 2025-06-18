# -*- coding:utf-8 -*-
# @File    : __init__.py
# ***********************
from pathlib import Path

from comm.utils.readYaml import read_yaml_data
import os

# Gets the home directory path
ROOT_DIR = str(os.path.realpath(__file__)).split('config')[0].replace('\\', '/')

# Obtain the configuration file path
API_CONFIG = ROOT_DIR+'config/apiConfig.yml'    # ip header
RUN_CONFIG = ROOT_DIR+'config/runConfig.yml'    # Use case directory use case execution mechanism, etc
DB_CONFIG = ROOT_DIR+'config/dbConfig.yml'      # Database configuration

# Get the running configuration information
RC = read_yaml_data(RUN_CONFIG)
AC = read_yaml_data(API_CONFIG)
INTERVAL = RC['interval']    # Interface invocation interval
PROJECT_NAME = RC['project_name']     # Run item name
# The project uses the database type
DB_TYPE = AC[PROJECT_NAME]['dbType'].lower()
# whether using proxy
PROXY = AC[PROJECT_NAME]['proxy']
PROXIES = AC[PROJECT_NAME]['proxies']

if Path(ROOT_DIR+PROJECT_NAME).is_dir():
    # Interface data directory(.chlsj)
    DATA_DIR = ROOT_DIR+PROJECT_NAME+'/data'
    # Test data catalog(test_xxxxx.yaml)
    PAGE_DIR = ROOT_DIR+PROJECT_NAME+'/page'
    # Test script directory(aaaaa.py)
    TEST_DIR = ROOT_DIR+PROJECT_NAME+'/testcase'
else:
    # Interface data directory(.chlsj)
    DATA_DIR = ROOT_DIR+'PyDemo'+'/data'
    # Test data catalog(test_xxxxx.yaml)
    PAGE_DIR = ROOT_DIR+'PyDemo'+'/page'
    # Test script directory(aaaaa.py)
    TEST_DIR = ROOT_DIR+'PyDemo'+'/testcase'

# Test report directory(xml|html)
REPORT_DIR = ROOT_DIR + 'report'
# Test log directory
LOG_DIR = ROOT_DIR + 'logs'
# Upload file directory (Used to store files on the interface to be uploaded)
UPLOAD_DIR = ROOT_DIR + 'data_warehouse/upload/'
# Download file directory
DOWNLOAD_DIR = ROOT_DIR + 'data_warehouse/download/'


