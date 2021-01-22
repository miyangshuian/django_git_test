from automation_test.unit_api_test.login_information import Login_envirment
from automation_test.unit_api_test.common_mode import CommonMethod
from automation_test.unit_api_test.common_mode import Constant
from multiprocessing import Pool
import jsonpath

class Start_test(Login_envirment,CommonMethod):

	def get_cookies(self,user,type):
		header_cookies=self.get_login_token(user,type)
		return header_cookies

	def user_cookies(self,users):
		self.shigongfang_cookies = self.get_cookies(users['shigongfang']['fuzheren'],users['shigongfang']['account_type'])
		self.hualifang_cookies = self.get_cookies(users['hualifang']['fuzheren'],users['hualifang']['account_type'])
		self.qudaoshang_cookies = self.get_cookies(users['qudaoshang']['fuzheren'],users['qudaoshang']['account_type'])
		self.huayuansu_cookies = self.get_cookies(users['huayuansu']['fuzheren'],users['huayuansu']['account_type'])
		self.changshang_cookies = self.get_cookies(users['changshang']['fuzheren'],users['changshang']['account_type'])

	def assignment(self,api_information):
		mothod = api_information[2]
		api_url = api_information[1]
		login_info = api_information[3]
		body = api_information[4]
		hope = api_information[6]
		action = api_information[5]
		test_process = api_information[7]
		files_key = api_information[9]

		if login_info == Constant.common_sgf_role.value:
			headers = self.shigongfang_cookies
		elif login_info == Constant.common_hlf_role.value:
			headers = self.hualifang_cookies
		elif login_info == Constant.common_qds_role.value:
			headers = self.qudaoshang_cookies
		elif login_info == Constant.common_hys_role.value:
			headers = self.huayuansu_cookies
		else:
			headers = self.changshang_cookies

		if files_key:
			files = self.get_img(files_key)
		else:
			files = []

		response = self.send_request(mothod, api_url, headers, body, files=files)
		try:
			api_action = self.get_response_value(response, action)
			if str(api_action) == hope:
				value = (api_url, test_process, 'pass')
			else:
				value = (api_url, test_process, 'fail')
		except:
			value = (api_url, test_process, 'error')

		return value

	def start_debug(self,tab):
		print('=================开始测试================')
		api_informations=self.read_excle_one_sheet(tab)
		for api_information in api_informations:
			value = self.assignment(api_information)
			print(value)

	def start_test(self,sql,condition='all'):
		print('=================开始测试================')
		api_informations = self.query_mysql(sql, condition)
		values = [('测试接口', '测试场景', '测试结果')]
		if condition=='all':
			for api_information in api_informations:
				value=self.assignment(api_information)
				values.append(value)
		else:
			value=self.assignment(api_informations)
			values.append(value)

		self.write_excle(values)
		print('=============测试结果已保存=============')

def assignment_pool(host,headers,api_information):
	mothod = api_information[2]
	api_url = api_information[1]
	login_info = api_information[3]
	body = api_information[4]
	hope = api_information[6]
	action = api_information[5]
	test_process = api_information[7]
	files_key = api_information[9]
	send_request_pool=CommonMethod(host)
	api_action_pool = jsonpath

	if login_info == Constant.common_sgf_role.value:
		headers = headers['shigongfang']
	elif login_info == Constant.common_hlf_role.value:
		headers = headers['hualifang']
	elif login_info == Constant.common_qds_role.value:
		headers = headers['qudaoshang']
	elif login_info == Constant.common_hys_role.value:
		headers =headers['huayuansu']
	else:
		headers = headers['changshang']

	if files_key:
		files = self.get_img(files_key)
	else:
		files = []

	response = send_request_pool.send_request(mothod,api_url, headers, body, files=files)
	try:
		api_action = api_action_pool.jsonpath(response, action)[0]
		if str(api_action) == hope:
			value = (api_url, test_process, 'pass')
		else:
			value = (api_url, test_process, 'fail')
	except:
		value = (api_url, test_process, 'error')
	return value

if __name__ == '__main__':
	users_information = {
		'shigongfang': {'fuzheren': 'caoyuehua', 'account_type': 5, 'company_name': '河南平安实业有限公司', 'company_id': 174},
		'hualifang': {'fuzheren': 'zhangzihanghlf', 'caiwu': 'wangjialehys1', 'dingdan': 'chengzhefeng',
					  'shenpi': 'monica',
					  'account_type': 1, 'company_name': '深圳市华立方商业集团有限公司', 'company_id': 33},
		'qudaoshang': {'fuzheren': 'houdong', 'account_type': 4, 'company_name': '河南浩海商贸有限公司', 'company_id': 153},
		'huayuansu': {'fuzheren': 'duanye', 'caiwu': 'wangjialehys1', 'dingdan': 'wangjialehys1', 'shenpi': 'monica',
					  'account_type': 2, 'company_name': '华元素采购（深圳）有限公司', 'company_id': 34},
		'changshang': {'fuzheren': 'nuobeier', 'other': 'SKS123', 'account_type': 3, 'company_name': '杭州诺贝尔陶瓷有限公司',
					   'company_id': 86}
	}
	mysql_host = '192.168.188.12'
	mysql_db = 'epodb_test_robotization'
	host = 'http://192.168.188.14:10157'
	sql=f"select * from API_information "
	api_test=Start_test(host)
	print('=================连接数据库=================')
	api_test.connect_mysql(mysql_host,mysql_db)
	print('=================登录账户=================')
	def onlyone():
		api_test.user_cookies(users_information)
		api_test.start_test(sql)

	def manypool():
		headers={
			'shigongfang':api_test.get_cookies(users_information['shigongfang']['fuzheren'],users_information['shigongfang']['account_type']),
			'hualifang':api_test.get_cookies(users_information['hualifang']['fuzheren'],users_information['hualifang']['account_type']),
			'qudaoshang':api_test.get_cookies(users_information['qudaoshang']['fuzheren'],users_information['qudaoshang']['account_type']),
			'huayuansu':api_test.get_cookies(users_information['huayuansu']['fuzheren'],users_information['huayuansu']['account_type']),
			'changshang':api_test.get_cookies(users_information['changshang']['fuzheren'],users_information['changshang']['account_type'])}
		api_informations = api_test.query_mysql(sql, 'all')
		pool = Pool()
		results=[]
		for api_information in api_informations:
			results.append(pool.apply_async(assignment_pool, (host,headers,api_information,)))
		pool.close()
		pool.join()
		values = [('测试接口', '测试场景', '测试结果')]+[result.get() for result in results]
		api_test.write_excle(values)

	onlyone()
	# manypool()

	# automation_test.user_cookies(users_information)
	# automation_test.start_debug(2)