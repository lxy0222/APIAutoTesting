
import re


class SoapParser:
	def get_soap_body (self, xml):
		xml = xml.decode('utf-8')
		searchObj = re.search( r'<soapenv:Body>(.*)</soapenv:Body>', xml, re.M|re.I)
		return searchObj.group(1)
		
	def get_element_body_by_name (self, xml, elementName):
		xml = xml.decode('utf-8')
		searchObj = re.search( r'<' + elementName + '>(.*)</' + elementName + '>', xml, re.M|re.I)
		if None == searchObj:
			return None
		else:
			return searchObj.group(1)
		
	def get_soap_error_message (self, xml):
		xml = xml.decode('utf-8')
		searchObj = re.search( r'<message>(.*)</message>', xml, re.M|re.I)
		return searchObj.group(1)
		
	def get_first_element_body_by_name (self, xml, elementName):
		xml = xml.decode('utf-8')
		searchObj = re.search( r'<' + elementName + '>([0-9]*)</' + elementName + '>', xml, re.M|re.I)
		return searchObj.group(1) 
		
	def get_all_element_body_by_name(self, xml, elementName):
		xml = xml.decode('utf-8')
		pattern = re.compile(r'<' + elementName + '>([\w\s]*)</' + elementName + '>')
		result = pattern.findall(xml)
		return result


import json
import xmltodict


def xml_to_dict(xml_dic=None):
	# xml解析器
	xml_par = xmltodict.parse(xml_dic)
	# 通过dumps()方法转换成json,格式化json，index=1
	json_dic = json.dumps(xml_par, indent=1)
	# 返回直接把null值替换成‘’
	return json_dic.replace("null", "''")


if __name__ == '__main__':
	sop = b'<?xml version=\'1.0\' encoding=\'UTF-8\'?><soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"><soapenv:Header /><soapenv:Body><service:readFinancialSummaryResponse xmlns="http://mercury.com/ppm/fm/1.0" xmlns:service="http://mercury.com/ppm/fm/service/1.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><service:financialSummary xmlns="http://mercury.com/ppm/fm/1.0" xmlns:service="http://mercury.com/ppm/fm/service/1.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><id>32773</id><name>nested_proposal</name><parent><parentType>PROPOSAL</parentType><parentIdentifier><id>31818</id></parentIdentifier></parent><localCurrencyCode>USD</localCurrencyCode><baseCurrencyCode>USD</baseCurrencyCode><approvedBudgets /><forecastActual><id>32773</id><isCapexOpexEnabled>false</isCapexOpexEnabled><actualRollupCode>MANUAL</actualRollupCode><lines /><userData /><periodSum /></forecastActual><benefit><id>32773</id><lines /><userData /><periodSum /></benefit><snapshots /><discountRate>10.0</discountRate><npv>0.0</npv><tnr>0.0</tnr></service:financialSummary></service:readFinancialSummaryResponse></soapenv:Body></soapenv:Envelope>'
	print(SoapParser().get_soap_body(sop))
	print(xml_to_dict(sop))