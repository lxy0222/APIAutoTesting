# -*- coding:utf-8 -*-
# @Time    : 2021/07/10
# @Author  : Xuanyu Liu
# @File    : randomly.py
# *************************
import string
import random
import datetime

from dateutil.relativedelta import relativedelta
from faker import Faker


def generate_bank_card():
	"""
		Generate random bank card numbers
	"""
	faker = Faker(locale='zh_CN')
	return faker.credit_card_number()


def generate_email():
	"""
	Generate a random email number
	"""
	faker = Faker(locale='zh_CN')
	return random_str(4)+faker.free_email()


def generate_company():
	"""
	Generate a random company name
	"""
	faker = Faker(locale='zh_CN')
	return faker.company_prefix() + random_str(5) + '测试' + faker.company_suffix()


def generate_name():
	"""
	Generate random name
	"""
	faker = Faker(locale='en_US')
	return faker.name()


def generate_first_name():
	"""
	Generate a random first name
	"""
	faker = Faker(locale='en_US')
	return faker.first_name()


def generate_last_name():
	"""
	Generate a random last name
	"""
	faker = Faker(locale='en_US')
	return faker.last_name()


def generate_unreal_phone():
	"""
	Generate a non-existent mobile phone number
	"""
	phone = random.choice(['100', '110', '120']) + ''.join(random.choice('0123456789') for _ in range(8))
	return phone


def random_str(str_len):
	"""Generate a specified number of random characters from a-za-Z0-9

	:param str_len: String length
	:return:
	"""
	try:
		str_len = int(str_len)
	except ValueError:
		raise Exception("Failed to call random character, the [%s] length argument is incorrect!" % str_len)
	strings = ''.join(random.sample(string.hexdigits, +str_len))
	return strings


def random_int(scope):
	"""Get random integer data

	:param scope:
	:return:
	"""
	try:
		start_num, end_num = scope.split(",")
		start_num = int(start_num)
		end_num = int(end_num)
	except ValueError:
		raise Exception("Failed to call random integer with incorrect range parameter of [%s]!" % str(scope))
	if start_num <= end_num:
		number = random.randint(start_num, end_num)
	else:
		number = random.randint(end_num, start_num)
	return number


def random_float(data):
	"""Gets random floating-point data

	:param data: array
	:return:
	"""
	try:
		start_num, end_num, accuracy = data.split(",")
		start_num = int(start_num)
		end_num = int(end_num)
		accuracy = int(accuracy)
	except ValueError:
		raise Exception("Failed to call random floating-point number, [%s] range argument or precision error!" % data)

	if start_num <= end_num:
		number = random.uniform(start_num, end_num)
	else:
		number = random.uniform(end_num, start_num)
	number = round(number, accuracy)
	return number


def random_choice(data):
	"""Gets the array random value

	:param data: array
	:return:
	"""
	_list = data.split(",")
	each = random.choice(_list)
	return each


def get_date_mark(now, mark, num):
	if 'y' == mark:
		return now + relativedelta(years=num)
	elif 'm' == mark:
		return now + relativedelta(months=num)
	elif 'd' == mark:
		return now + relativedelta(days=num)
	elif 'h' == mark:
		return now + relativedelta(hours=num)
	elif 'M' == mark:
		return now + relativedelta(minutes=num)
	elif 's' == mark:
		return now + relativedelta(seconds=num)
	else:
		raise Exception("Date field identification [%s] error, please use [year y, month m, day d, hour h, minute M, second s] identification!" % mark)


def generate_date(expr=''):
	"""Generate date objects (without time, minute and second)

	:param expr: Date expressions such as "d-1" represent date minus 1
	:return:
	"""
	today = datetime.date.today()
	if expr:
		try:
			mark = expr[:1]
			num = int(expr[1:])
		except (TypeError, NameError):
			raise Exception("Call to generate date failed, date expression [%s] is incorrect!" % expr)
		return get_date_mark(today, mark, num)
	else:
		return today


def generate_year(expr=''):
	"""Generate date objects (without time, minute and second)

	:param expr: Date expressions such as "d-1" represent date minus 1
	:return:
	"""
	data = generate_date(expr)
	return str(data)[0:4]

def generate_datetime(expr=''):
	"""Generate date-time objects (including time minutes and seconds)

	:param expr: Date expressions such as "d-1" represent date minus 1
	:return:
	"""
	now = datetime.datetime.now().replace(microsecond=0)
	if expr:
		try:
			mark = expr[:1]
			num = int(expr[1:])
		except (TypeError, NameError):
			raise Exception("Call to generate date failed, date expression [%s] is incorrect!" % expr)
		return get_date_mark(now, mark, num)
	else:
		return now


def generate_timestamp(expr=''):
	"""Generate timestamp (13 bits)

	:param expr: Date expressions such as "d-1" represent date minus 1
	:return:
	"""
	datetime_obj = generate_datetime(expr)
	return int(datetime.datetime.timestamp(datetime_obj)) * 1000


def generate_guid():
	"""Generate Guids based on MAC address + timestamp + random number

	:param:
	:return:
	"""
	import uuid
	return str(uuid.uuid1()).upper()


def generate_wxid():
	"""The fake wechat ID is generated based on the AUTO ID +26 English letter case + number

	:param:
	:return:
	"""
	return 'AUTO' + ''.join(random.sample(string.ascii_letters + string.digits, 24))


def generate_noid(expr=''):
	"""Generate fake ID cards based on 6 random numbers + date of birth +4 random numbers
	:return:
	"""
	birthday = generate_date(expr)
	birthday = str(birthday).replace('-', '')
	return int(str(random.randint(100000, 999999)) + birthday + str(random.randint(1000, 9999)))


def generate_phone():
	"""基Generate pseudo phone numbers based on three major carrier segments + random numbers

	:param:
	:return:
	"""
	ctcc = [133,153,173,177,180,181,189,191,193,199]
	cucc = [130,131,132,155,156,166,175,176,185,186,166]
	cmcc = [134,135,136,137,138,139,147,150,151,152,157,158,159,172,178,182,183,184,187,188,198]
	begin = 10 ** 7
	end = 10 ** 8 - 1
	prefix = random.choice(ctcc+cucc+cmcc)
	return str(prefix) + str(random.randint(begin, end))


from calendar import monthrange


def convert_month_to_date(month_text, is_end_time=False):
	# 将月份文本转换为日期对象
	date_obj = datetime.datetime.strptime(month_text, "%B %Y")

	if is_end_time:
		# 获取该月份的最后一天
		last_day = monthrange(date_obj.year, date_obj.month)[1]
		date_obj = date_obj.replace(day=last_day)

	# 格式化日期为 'YYYY-MM-DD' 的字符串
	formatted_date = date_obj.strftime("%Y-%m-%d")
	return formatted_date


if __name__ == '__main__':
	# Simple random data
	print(random_str(16))
	print(random_int("100,200"))
	print(random_float("200,100,5"))
	print(random_choice("aaa,bbb,ccc"))

	# Generate date data
	print(generate_date())
	print(generate_datetime())
	print(generate_date('m+3'))
	print(generate_datetime('d+3'))
	print(generate_timestamp('s+100'))
	print(generate_noid('y-18'))

	# Generate common data
	print(generate_guid())
	print(generate_wxid())
	print(generate_noid())
	print(generate_phone())

	print(generate_email())
	print(generate_bank_card())
	print(generate_first_name())
	print(generate_last_name())
	print(generate_year('y+2'))
	# 示例用法

	# 示例用法
	month_text = "February 2023"
	formatted_start_date = convert_month_to_date(month_text)
	formatted_end_date = convert_month_to_date(month_text, is_end_time=True)
	print(f"Start Date: {formatted_start_date}")
	print(f"End Date: {formatted_end_date}")
