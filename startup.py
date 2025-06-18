# -*- coding:utf-8 -*-
# @File    : startup.py
import os
import re
import sys

import jsonpath
import pytest
from comm.script.writeLogs import logger


if __name__ == '__main__':

    from comm.script import writeCasev2
    from config import *

    if RC['auto_switch'] == 3:
        logger.info("According to interface capture data, automatically generate test cases and test scripts, but do not run tests!")
        writeCasev2.write_case(DATA_DIR, auto_yaml=True)
        sys.exit(0)

    elif RC['auto_switch'] == 2:
        logger.info("According to the interface capture data, automatically generate test cases and test scripts, and then run the test!")
        writeCasev2.write_case(DATA_DIR, auto_yaml=True)

    elif RC['auto_switch'] == 1:

        if not os.path.exists(RC['scan_dir']):
            RC['scan_dir'] = PAGE_DIR
        logger.info("Automatically generate test scripts based on hand-written use cases, and then run the tests!")
        writeCasev2.write_case(RC['scan_dir'], auto_yaml=False)

    else:
        logger.info("Do not enable automatic test case generation function, will run the test directly!")

    args_list = ['-vs', TEST_DIR,
                 '-n', str(RC['process']),
                 '-m', 'not {}'.format("tag"),
                 '--reruns', str(RC['reruns']),
                 '--maxfail', str(RC['maxfail']),
                 '--alluredir', REPORT_DIR+'/xml',
                 '--clean-alluredir']

    if RC['pattern']:
        args_list += ['-k ' + str(RC['pattern'])]
    try:
        # run script
        test_result = pytest.main(args_list)

        # report
        cmd = 'allure generate --clean %s -o %s ' % (REPORT_DIR+'/xml', REPORT_DIR+'/html')
        os.system(cmd)
    except Exception as e:
        raise e

