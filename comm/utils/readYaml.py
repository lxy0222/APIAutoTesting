# -*- coding:utf-8 -*-
# @File    : readYaml.py
# ***********************


def read_yaml_data(yaml_file):
	"""Read yaml file data

	:param yaml_file: yaml file path
	:return:
	"""
	import yaml
	yaml_file = yaml_file.replace('\\', '/')
	with open(yaml_file, 'r', encoding="utf-8") as fr:
		return yaml.load(fr, Loader=yaml.SafeLoader)


def write_yaml_file(yaml_file, obj):
	"""Write the object to the yaml file

	:param yaml_file: yaml file path
	:param obj: data object
	:return:
	"""
	from ruamel import yaml
	with open(yaml_file, 'w', encoding='utf-8') as fw:
		yaml.dump(obj, fw, Dumper=yaml.RoundTripDumper, allow_unicode=True)


def rewrite_yaml_file(yaml_file, mode,  section, value):
	import yaml
	with open(yaml_file, encoding='utf-8') as fp:
		read_yml_str = fp.read()
		d = yaml.safe_load(read_yml_str)
	d[mode][section] = value
	with open(yaml_file, 'w', encoding='utf-8') as f:
		yaml.dump(d, f, allow_unicode=True)
