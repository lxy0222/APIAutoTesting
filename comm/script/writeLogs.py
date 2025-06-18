# -*- coding:utf-8 -*-
# @File    : writeLogs.py
# ************************
import os
import sys
import logging
import time
import inspect

from config import LOG_DIR


class CustomLogger:
    _instance = None

    @staticmethod
    def get_instance(log_path):
        if CustomLogger._instance is None:
            CustomLogger(log_path)
        return CustomLogger._instance

    def __init__(self, log_path):
        if CustomLogger._instance is not None:
            raise Exception("CustomLogger is a singleton. Use CustomLogger.get_instance() to get the instance.")

        # Define default log path and log names
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        runtime = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        logfile = os.path.join(log_path, runtime + '.log')
        logfile_err = os.path.join(log_path, runtime + '_error.log')

        # Step 1: Initialize the logger object and set log level
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers = []

        # Step 2: Create a handler for writing debug logs to a file
        fh = logging.FileHandler(logfile, mode='a+', encoding='utf-8')  # Set encoding to 'utf-8'
        fh.setLevel(logging.DEBUG)

        # Step 3: Create a handler for writing error logs to a file
        fh_err = logging.FileHandler(logfile_err, mode='a+', encoding='utf-8')  # Set encoding to 'utf-8'
        fh_err.setLevel(logging.ERROR)

        # Step 4: Create a handler for outputting info logs to the console
        sh = logging.StreamHandler(sys.stdout)
        sh.setLevel(logging.INFO)

        # Step 5: Define the output format for the handlers
        formatter = logging.Formatter("%(asctime)s - %(filename)s - %(levelname)s: %(message)s")
        fh.setFormatter(formatter)
        fh_err.setFormatter(formatter)
        sh.setFormatter(formatter)

        # Step 6: Add the handlers to the logger
        self.logger.addHandler(fh)
        self.logger.addHandler(fh_err)
        self.logger.addHandler(sh)

        CustomLogger._instance = self

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(f"file：{self.get_caller_filename()} - {message}")

    def warning(self, message):
        self.logger.warning(f"file：{self.get_caller_filename()} - {message}")

    def error(self, message):
        self.logger.error(f"file：{self.get_caller_filename()} - {message}")

    def critical(self, message):
        self.logger.critical(f"file：{self.get_caller_filename()} - {message}")

    def exception(self, message):
        self.logger.exception(f"file：{self.get_caller_filename()} - {message}")

    @staticmethod
    def get_caller_filename():
        frame = inspect.currentframe()
        frame = frame.f_back.f_back  # Skip the get_caller_filename and logger function calls
        filename = inspect.getframeinfo(frame).filename
        return os.path.basename(filename)


logger = CustomLogger(LOG_DIR)
