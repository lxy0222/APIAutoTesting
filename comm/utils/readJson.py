# -*- coding:utf-8 -*-
# @File    : readJson.py
# ***********************
import json
import re

import jsonpath
from jsonpath_ng import parse


def read_json_data(json_file):
	"""Read the json file data

	:param json_file: json file path
	:return:
	"""
	with open(json_file, "r", encoding="utf-8") as fr:
		return json.load(fr)


def write_json_file(json_file, obj):
	"""Write object to a json file

	:param json_file: json file path
	:param obj: data object
	:return:
	"""
	with open(json_file, "w", encoding='utf-8') as fw:
		json.dump(obj, fw, ensure_ascii=False, indent=4)


def update_json(dic_json, key_words):
	"""
	json field replacement update
	"""
	if key_words.get("kwargs"):
		for key, value in key_words.get("kwargs").items():
			param = dic_json['parameter']
			if isinstance(param, str):
				pattern = rf'<{key}>(.*?)</{key}>'
				matches = re.findall(pattern, param)
				for match in matches:
					param = param.replace(match, value)
				dic_json['parameter'] = param
			else:
				try:
					paths = jsonpath.jsonpath(dic_json, key, result_type="PATH")
					# 使用更新路径更新对应的值
					parse1 = parse(paths[0])
					parse1.update(dic_json, value)
				except Exception as e:
					raise e
	else:
		if not key_words:
			return dic_json
		for key, value in dic_json.items():
			if key in key_words:
				dic_json[key] = key_words[key]
				del key_words[key]
				if len(key_words) == 0:
					break
			elif isinstance(value, dict):
				update_json(value, key_words)
				if len(key_words) == 0:
					break
	return dic_json

