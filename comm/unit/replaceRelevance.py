# -*- coding:utf-8 -*-
# @File    : replaceRelevance.py
# ****************************
from comm.script.writeLogs import logger
import re
from comm.utils.randomly import *
from comm.unit.GlobalVariable import GlobalData

pattern_var = r"\${(.*?)}"
pattern_eval = r"\$Eval\((.*?)\)"
pattern_str = r'\$RandStr\(([0-9]*?)\)'
pattern_int = r'\$RandInt\(([0-9]*,[0-9]*?)\)'
pattern_choice = r"\$RandChoice\((.*?)\)"
pattern_float = r'\$RandFloat\(([0-9]*,[0-9]*,[0-9]*)\)'
pattern_phone = r'\$GenPhone\(\)'
pattern_guid = r'\$GenGuid\(\)'
pattern_wxid = r'\$GenWxid\(\)'
pattern_noid = r'\$GenNoid\((.*?)\)'
pattern_date = r'\$GenDate\((.*?)\)'
pattern_datetime = r'\$GenDatetime\((.*?)\)'
pattern_timestamp = r'\$GenTimeStamp\((.*?)\)'
pattern_name = r'\$GenName\((.*?)\)'
pattern_first_name = r'\$GenFirstName\((.*?)\)'
pattern_last_name = r'\$GenLastName\((.*?)\)'
pattern_unreal_phone = r'\$GenUnrealPhone\((.*?)\)'
pattern_company = r'\$GenCompany\((.*?)\)'
partern_email = r'\$GenEmail\((.*?)\)'
partern_bank_card = r'\$GenBankCard\((.*?)\)'


def replace_pattern(pattern, value):
	"""Replacement regular expression

	:param pattern: regular expression
	:param value: matching value
	:return:
	"""
	patterns = pattern.split('(.*?)')
	return ''.join([patterns[0], value, patterns[-1]])


def replace_relevance(param, relevance=None):
	"""Replace variable association values
	:param param: Parameter object
	:param relevance: Associated object
	:return:
	"""
	global pattern
	result = re.findall(pattern_var, str(param))
	if (not result) or (not relevance):
		pass
	else:
		for each in result:
			try:
				relevance_index = 0
				if isinstance(relevance[each], list):
					try:
						param = re.sub(pattern, relevance[each][relevance_index], param, count=1)
						relevance_index += 1
					except IndexError:
						relevance_index = 0
						param = re.sub(pattern, relevance[each][relevance_index], param, count=1)
						relevance_index += 1
				value = relevance[each]
				pattern = re.compile(r'\${' + each + '}')
				try:
					param = re.sub(pattern, str(value), param)
					if not isinstance(value, str) and not isinstance(value, int):
						param = eval(param)
				except TypeError as e:
					param = param
					raise e
			except KeyError:
				continue
	return param


def replace_eval(param):
	"""Replace the result of an eval expression

	:param param: Parameter object
	:return:
	"""
	result = re.findall(pattern_eval, str(param))
	if not result:
		pass
	else:
		for each in result:
			try:
				if 'import' in each:
					raise Exception('An illegal identity import exists')
				else:
					value = str(eval(each))
					param = re.sub(pattern_eval, value, param)
			except KeyError as e:
				raise Exception('Failed to get the value [%]！\n%'.format(param, e))
			except SyntaxError:
				pass
	return param


def replace_random(param):
	"""Replace random method parameter values

	:param param:
	:return:
	"""
	int_list = re.findall(pattern_int, str(param))
	str_list = re.findall(pattern_str, str(param))
	choice_list = re.findall(pattern_choice, str(param))
	guid_list = re.findall(pattern_guid, str(param))
	noid_list = re.findall(pattern_noid, str(param))
	phone_list = re.findall(pattern_phone, str(param))
	wxid_list = re.findall(pattern_wxid, str(param))
	date_list = re.findall(pattern_date, str(param))
	datetime_list = re.findall(pattern_datetime, str(param))
	timestamp_list = re.findall(pattern_timestamp, str(param))
	name_list = re.findall(pattern_name, str(param))
	first_name_list = re.findall(pattern_first_name, str(param))
	last_name_list = re.findall(pattern_last_name, str(param))
	unreal_phone_list = re.findall(pattern_unreal_phone, str(param))
	company_list = re.findall(pattern_company, str(param))
	email_list = re.findall(partern_email, str(param))
	bankcard_list = re.findall(partern_bank_card, str(param))

	if len(bankcard_list):
		for each in bankcard_list:
			param = re.sub(partern_bank_card, str(generate_bank_card()), param, count=1)

	if len(email_list):
		for each in email_list:
			param = re.sub(partern_email, str(generate_email()), param, count=1)

	if len(company_list):
		for each in company_list:
			param = re.sub(pattern_company, str(generate_company()), param, count=1)

	if len(unreal_phone_list):
		for each in unreal_phone_list:
			param = re.sub(pattern_unreal_phone, str(generate_unreal_phone()), param, count=1)

	if len(name_list):
		for each in name_list:
			param = re.sub(pattern_name, str(generate_name()), param, count=1)

	if len(first_name_list):
		for each in first_name_list:
			param = re.sub(pattern_first_name, str(generate_first_name()), param, count=1)

	if len(last_name_list):
		for each in last_name_list:
			param = re.sub(pattern_last_name, str(generate_last_name()), param, count=1)

	if len(str_list):
		for each in str_list:
			param = re.sub(pattern_str, str(random_str(each)), param, count=1)

	if len(int_list):
		for each in int_list:
			param = re.sub(pattern_int, str(random_int(each)), param, count=1)

	if len(choice_list):
		for each in choice_list:
			param = re.sub(pattern_choice, str(random_choice(each)), param, count=1)

	if len(date_list):
		for each in date_list:
			param = re.sub(pattern_date, str(generate_date(each)), param, count=1)

	if len(datetime_list):
		for each in datetime_list:
			param = re.sub(pattern_datetime, str(generate_datetime(each)), param, count=1)

	if len(timestamp_list):
		for each in timestamp_list:
			param = re.sub(pattern_timestamp, str(generate_timestamp(each)), param, count=1)

	if len(noid_list):
		for each in noid_list:
			param = re.sub(pattern_noid, str(generate_noid(each)), param, count=1)

	if len(phone_list):
		for i in phone_list:
			param = re.sub(pattern_phone, str(generate_phone()), param, count=1)

	if len(guid_list):
		for i in guid_list:
			param = re.sub(pattern_guid, generate_guid(), param, count=1)

	if len(wxid_list):
		for i in wxid_list:
			param = re.sub(pattern_wxid, generate_wxid(), param, count=1)

	return param


def replace_global_data(param):
	pattern_var = r"\${(GD_.*?)}"
	result = re.findall(pattern_var, str(param))
	for each in result:
		pattern = re.compile(r'\${' + each + '}')
		param = re.sub(pattern, str(getattr(GlobalData.local_data.namespace, each, "${"+each+"}")), param)
	return param


def replace(param, relevance=None):
	"""Replace the associated data corresponding to the parameter

	:param param: Parameter object
	:param relevance: Associated object
	:return:
	"""
	if not param:
		pass
	elif isinstance(param, dict):
		for key, value in param.items():
			if isinstance(value, dict):
				param[key] = replace(value, relevance)
			elif isinstance(value, list):
				for index, sub_value in enumerate(value):
					param[key][index] = replace(sub_value, relevance)
			else:
				value = replace_global_data(value)
				value = replace_relevance(value, relevance)
				value = replace_random(value)
				value = replace_eval(value)
				param[key] = value

	elif isinstance(param, list):
		for index, value in enumerate(param):
			param[index] = replace(value, relevance)

	else:
		param = replace_global_data(param)
		param = replace_relevance(param, relevance)
		param = replace_random(param)
		param = replace_eval(param)

	return param


if __name__ == '__main__':
	print('替换变量并计算表达式：', replace('$Eval(${unitCode}*1000+1)', {'unitCode': 9876543210}))
	print('生成1-9之间的随机数：', replace('$RandInt(1,9)'))
	print('生成10位随机字符：', replace('$RandStr(10)'))
	print('从列表中随机选择：', replace('$RandChoice(a,b,c,d)'))
	print('生成一个伪手机号：', replace('$GenPhone()'))
	print('生成一个guid：', replace('$GenGuid()'))
	print('生成一个伪微信ID：', replace('$GenWxid()'))
	print('生成一个伪身份证：', replace('$GenNoid()'))
	print('生成一个18岁伪身份证：', replace("$GenNoid(y-18)"))
	print('生成下个月今天的日期：', replace("$GenDate(m+1)"))     # 2021-08-19
	print('生成昨天此时的时间：', replace("$GenDatetime(d-1)"))    # 2021-07-18 10:21:22
	print('生成不存在的手机号：', replace("$GenUnrealPhone()"))
	print('生成随机姓名：', replace("$GenName()"))
	print('生成随机公司名称：', replace("$GenCompany()"))
	print('生成随机邮箱：', replace("$GenEmail()"))
	print('生成随机银行卡号：', replace("$GenBankCard()"))
	print('生成随机银行卡号：', replace("$GenTimeStamp()"))
	print('替换变量并计算表达式：', replace('$Eval(8/2)'))
