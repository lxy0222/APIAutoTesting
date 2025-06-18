# -*- coding:utf-8 -*-
# @File    : readRelevance.py
# ****************************
from comm.script.writeLogs import logger
import re

__relevance = ""


def get_value(data, value):
    """Gets the value in the data

    :param data:
    :param value:
    :return:
    """
    global __relevance
    if isinstance(data, dict):
        if value in data:
            __relevance = data[value]
        else:
            for key in data:
                __relevance = get_value(data[key], value)
    elif isinstance(data, list):
        for key in data:
            if isinstance(key, dict):
                __relevance = get_value(key, value)
                break
    return __relevance


def get_relevance(data, relevance_list, relevance=None):
    """Gets a list of association keys

    :param data:
    :param relevance_list:
    :param relevance:
    :return:
    """

    relevance_list = re.findall(r"\${(.*?)}", str(relevance_list))
    relevance_list = list(set(relevance_list))
    logger.debug("Gets a list of association keys:\n%s" % relevance_list)
    if (not data) or (not relevance_list):
        return relevance

    if not relevance:
        relevance = dict()
    for each in relevance_list:
        if each in relevance:
            pass
            # if isinstance(relevance[each], list):
            #     a = relevance[each]
            #     a.append(relevance_value)
            #     relevance[each] = a
            # else:
            #     a = relevance[each]
            #     b = list()
            #     b.append(a)
            #     b.append(relevance_value)
            #     relevance[each] = b
        else:
            relevance[each] = get_value(data, each)
    logger.debug("Extract the association key object:\n%s" % relevance)
    return relevance
