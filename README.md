# 使用前准备：
    1、安装配置python3.6版本及以上环境和pycharm
        安装与配置可参考：https://blog.csdn.net/ling_mochen/article/details/79314118/
    2、安装allure环境 并配置环境变量 （allure安装包在data_warehouse/source目录下）
        安装与配置可参考：https://www.cnblogs.com/strive-2020/p/12630067.html
    3、pip install -r requirements.txt 
    （安装不成功的进行单个手动添加，或者更换pip源：pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple）
    4、去掉allure报告title后的参数化显示：文件位置：Lib\site-packages\allure_pytest\listener.py （第三方包所在的LIb目录） 
    将test_result.parameters.extend(........) 中参数改成空列表就行了[],修改后-test_result.parameters.extend([])

**此框架是基于Python3+pyTest+Requests+Allure+Yaml+Json实现全链路接口自动化测试。**

# 主要流程：

## 1）抓包的接口
解析接口数据包 ->生成接口基础配置(yml) ->生成测试用例(yaml+json) ->生成测试脚本(.py) ->运行测试(pytest) ->生成测试报告(allure)
## 2）手工编写的接口用例
手工根据规则编写测试用例(yaml+json) ->生成测试脚本(.py) ->运行测试(pytest) ->生成测试报告(allure)

# 测试流程：

初始化请求 ->处理接口基础信息 ->读取前置接口用例 ->发送前置接口 ->处理当前接口数据 ->发送当前接口 ->检查接口返回

# 接口自动化测试框架介绍：

## 关于接口依赖：
    支持前置接口预置，填写前置接口相对路径即可，如果存在数据依赖关系，此时你也仅需要填写前置接口对应的参数值，本框架将自动为你调用和替换关联数据。
			1、前置接口配置：
			  1）项目文件的page目录下有comeCase.yaml 公用测试用例文件，前置写这个文件类的接口时，配置： premise: /commonCase.yaml xxx接口 测试数据索引(从0开始);
			  2）也支持填写已有接口，从测试文件中去数据，配置：premise: /xxx/xxxx.yaml _ 测试数据索引(从0开始)
			2、前置接口数据依赖：
			  引用见下面---_关于参数化_
			3、test_info和case_data的premise优先级：
			    两个同时配置，优先case_data

## 关于测试数据：
    本框架采用yaml记录接口基本信息，当请求参数和结果较大时，将单独保存到json文件中，解决各类数据的错综复杂问题。

## 关于参数化：
    本框架采用常用工具使用的变量标识 ${var} ，通过正则表达式，自动检索变量，自动为你替换变量，并且为你提供多种函数助手【$RandInt()、$GenGuid()】等，生成一些随机的伪数据，解决各种数据问题。
            参数引用：
                1)前置接口的请求参数以及配置文件里的参数 ${xxx}
                2)前置接口的响应参数
                    response：{'code': 0, 'msg': 'OK', 'id': 100100, 'data': {'id': 127409, 'member_id': 1236921938, 'title': '新增一个项目', 'amount': 6300.0, 'loan_rate': 12.0, 'loan_term': 12, 'loan_date_type': 1, 'bidding_days': 5, 'create_time': '2021-10-09 11:05:46.0', 'bidding_start_time': None, 'full_time': None, 'status': 1}, 
                    'copyright': 'Copyright © 2017-2020  All Rights Reserved', 
                    'parameter': {'member_id': '1236921938', 'title': '新增一个项目', 'amount': 6300.0, 'loan_rate': 12.0, 'loan_term': 12, 'loan_date_type': 1, 'bidding_days': 5}}
                   例：要引用data下的id ${data_id} 以节点加_进行引用
                       要引用无父节点的就直接${code}
                3)数据库断言的时候不用遵循父节点的写法 直接${id} 如果遇到重复key只会引用第一个匹配的key，如果需要引用有父节点的可以联系我帮你修改一下
## 关于自定义函数调用
    以func_开头的自定义函数可进行传参调用，会自动进行查找，在函数体内需要返回调用结果
    引用方法 param: func_xxx{"params1":"参数一","params2":"参数二"}   函数名和传入的参数之间不能用空格

## 关于用例执行：
    本框架利用pytest扩展库，支持多线程模式、失败用例重试、用例模糊匹配等。

## 关于数据校验：本框架支持多种校验方式(5种)
	1） no_check：不做任何校验
	    例：
              check_body:
                check_type: no_check
                expected_code: 200（随意写value也可空着，但key必须保留）
                expected_result: 随意写value也可空着，但key必须保留

	2） check_code：仅校验接口返回码code
	    例：
              check_body:
                check_type: check_code
                expected_code: 200
                expected_result: 随意写value也可空着，但key必须保留

	3） check_json：校验接口返回码code，并进行json格式比较及校验返回结果（默认方式）
	    例：
              check_body:
                check_type: check_json
                expected_code: 200
                expected_result:
                  - ["gt", "code", -1]
                  - ["not_none", "message", "SUCCESS"]
                  - ["!=", "$..signatories", 2]

	4） entirely_check：校验接口返回码code，并进行完整比较返回结果
	    例：
              check_body:
                check_type: entirely_check
                expected_code: 200
                expected_result: {'code': 0, 'msg': 'OK'}

	5） regular_check：校验接口返回码code，并进行正则匹配返回结果
	    例：
              check_body:
                check_type: regular_check
                expected_code: 200
                expected_result: 
                   - "'code': 0"
                   - SUCCESS
	
	6） check_db：数据库校验
	    例：
              check_db:
                  - check_type: check_db
                    execute_sql: SELECT * FROM loan WHERE id ='${id}'
                    expected_result:
                      - amount: ${amount}  （字段名和值）
                    expected_num: 1  （查询结果行数校验）
                    
## 关于环境切换：
    本框架支持环境切换，只需增加修改配置文件
	1）默认项目名称：PyDemo （用于大部分项目支持）
	2）如果有项目对断言以及用例修改校大，可以复制PyDemo项目，重新生成一个项目包，如：PyDemoFW ，没有复制新的项目包会默认使用PyDemo项目的数据
	3）修改配置：
		- apiConfig.yaml 【项目配置】 复制一份默认项目配置，在文件下粘贴，修改键名为你需要运行的项目名；
		- dbConfig.yaml 【数据库配置】同上
		- requestConfig.yaml 【处理后写入的数据键值对】同上 这里的值不需要去修改，运行项目时后自动修改，可根据需求，可不用此配置
		- runConfig.yaml 【运行配置】 对应修改项目名，其他内容按需修改


# 运行配置说明：

    运行项目名 project_name: PyDemo 
    
    运行模式: auto_switch: 2
    
    0 - 不开启自动生成测试用例功能，将直接运行测试
    
    1 - 根据手工编写用例，自动生成测试脚本，然后运行测试
    
    2 - 根据接口抓包数据，自动生成测试用例和测试脚本，然后运行测试
    
    3 - 根据接口抓包数据，自动生成测试用例和测试脚本，但不运行测试
    
    注意：目前解析仅支持(.chlsj)格式，请使用Charles工具抓包导出JSON Session File
    
    扫描测试用例目录（且仅当auto_switch=1时有用） scan_dir:
    
    使用模糊匹配测试用例（空则匹配所有） pattern:
    
    执行并发线程数（0表示不开启） process: 0
    
    失败重试次数（0表示不重试） reruns: 0
    
    本轮测试最大允许失败数（超出则立即结束测试） maxfail: 20
    
    接口调用间隔时间（s） interval: 1


--- 
---
版权归 xuanyu liu 所有示例的接口仅做参考，不可进行压测并发调用

