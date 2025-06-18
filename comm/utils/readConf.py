# -*- coding:utf-8 -*-
# @File    : readConf.py
# ***********************
import codecs
import configparser


class ReadConf:

    def __init__(self, cfg_path):
        """
        Initialize the configuration file
        :param cfg_path:
        """
        fd = open(cfg_path.replace('\\', '/'), encoding='utf-8')
        data = fd.read()
        # The prefix of the configuration file is removed
        if data[:3] == codecs.BOM_UTF8:
            data = data[3:]
            files = codecs.open(cfg_path, "w")
            files.write(data)
            files.close()
        fd.close()
        self.cf = configparser.ConfigParser()
        self.cf.read(cfg_path, encoding='utf-8-sig')

    def get_sections(self):
        """
        Get all entries
        :return:
        """
        return self.cf.sections()

    def get_items(self, section):
        """
        Gets all key - value pairs under a specified entry
        :param section:
        :return:
        """
        return self.cf.items(section)

    def get_options(self, section):
        """
        Gets all key values under a specified entry
        :param section:
        :return:
        """
        return self.cf.options(section)

    def get_value(self, section, option):
        """
        Gets the value of the specified key for the specified entry
        :param section:
        :param option:
        :return:
        """
        return self.cf.get(section, option)

    def has_section(self, section):
        """
        Returns whether the specified entry exists
        :param section:
        :return:
        """
        return self.cf.has_section(section)

    def has_option(self, section, option):
        """
        Returns whether the specified key exists for the specified entry
        :param section:
        :param option:
        :return:
        """
        return self.cf.has_option(section, option)
