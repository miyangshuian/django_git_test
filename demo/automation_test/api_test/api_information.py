# -*- coding:utf-8 -*-
import requests, time, datetime, json, os,sys
from jsonpath import jsonpath
from automation_test.conn_mysql import Operation_mysql
from urllib.request import quote


class All_api():

	def __init__(self, host):
		self.environment = host
		self.session = requests.Session()
		self.sys=sys

	def send_request(self, method, url, headers, params={}, files=[], status="form-data"):
		try:
			url = f"{self.environment}{url}"
			if method == "get":
				response = self.session.get(url, headers=headers["header"])

			else:
				if status == "form-data":
					response = self.session.post(url, headers=headers["header"], data=params, files=files)
				else:
					response = self.session.post(url, headers=headers["header"], json=params, files=files)
			print(response.status_code, response.json())
			time.sleep(0.3)

			return response
		except Exception as e:
			print(e.__str__(), method, url, params, files)

	def get_img(self, dict_keys):
		# 上传图片
		img_path = f"{os.path.dirname(os.path.abspath(__file__))}/123.jpg"
		file = []
		for dict_key in dict_keys:
			file.append((dict_key, open(f'{img_path}', 'rb')))
		return file

	def ptinfo(self,value):
		print(str(value).center(30,'-'))

	def get_permission_tree(self, headers):
		# 获取公司的权限树
		url = f'/bk/perm/get/member/permission/tree/'
		res = self.send_request('get', url, headers)

	def get_companys_id(self, headers, condition):
		# 获取用户可切换公司的ID
		url = f'/channel/business/get_self_companys/'
		res = self.send_request('get', url, headers)
		result = res.json()['data']
		res = list(filter(lambda x: condition == x['account_type'] and x['name'] != '个人账户', result))[0]
		return {'company_id': res['id'], 'company_name': res['name']}

	def all_company_deparment(self,headers):
		# 获取公司下所有部门
		url = f'/channel/department/all_company_deparment/'
		res = self.send_request('get', url, headers)
		return res

	def add_new_department(self,headers,name):
		# 新增部门
		url = f'/channel/department/get_add_edit_departmentInfo/'
		body = {'department_id': '', 'name': name,'parent_id':'','type':1}
		res = self.send_request('post', url, headers, params=body)
		return res

	def add_company(self, headers, company_id, phone):
		# 申请加入公司
		url = f'/channel/department/application_add/'
		body = {'company_id': [str(company_id)], 'name': [str(phone)]}
		res = self.send_request('post', url, headers, params=body)

	def get_apply_view(self, headers, company_id, phone):
		# 获取申请列表
		url = f'/channel/department/application_view/?company_id={company_id}&page=1&pagesize='
		res = self.send_request('get', url, headers)
		list_names = res.json()['data']
		res = list(filter(lambda x: phone == x['phone'], list_names))[0]
		return res['id']

	def agree_add_company(self, headers, apply_id, phone):
		# 同意成员加入公司
		url = '/channel/department/application_view/'
		body = {'department_id_list': ['00'], 'phone': [str(phone)], 'job': ['测试'], 'name': [str(phone)],
				'type': ['1'], 'id': [str(apply_id)], 'csrfmiddlewaretoken': headers['csrftoken']}
		res = self.send_request('post', url, headers, params=body)

	def get_department_id(self, headers):
		# 获取集团子公司ID
		url = f'/channel/department/department_list_web/?type=0'
		res = self.send_request('get', url, headers)
		department_id = res.json()['data']['company']['id']
		return department_id

	def add_personal_to_company(self, headers, phone_num, department_id):
		# 添加新用户到平台
		url = f'/channel/department/add_deparment_member/'
		body = {'department_id_list': [''], 'phone': [str(phone_num)], 'job': [''], 'name': [str(phone_num)],
				'company_id': [str(department_id)]}
		res = self.send_request('post', url, headers, params=body)

	def role_list(self, headers, phone_num):
		# 获取用户在组织架构中的ID
		url = f'/bk/perm/del/list/rolesUser/?search_key={phone_num}&page=1&page_size=10'
		res = self.send_request('get', url, headers)
		role_list_id = res.json()['data']['data_list'][0]['id']
		print('获取用户在组织架构中的ID:', role_list_id)
		return role_list_id

	def get_son_company(self, headers, role_list_id, company_id):
		# 授予用户组织权限
		url = f'/bk/perm/get/all/son/company/'
		body = {'company_id_list': [company_id], 'member_id': role_list_id}
		res = self.send_request('post', url, headers, params=body)

	def get_template_list(self, headers):
		# 获取公司权限模式
		url = '/bk/perm/template/list/'
		res = self.send_request('get', url, headers)
		response = list(filter(lambda x: x['status'], res.json()['data']))[0]
		return {'name': response['name'], 'id': response['id']}

	def member_rolelist(self, headers, phone):
		# 获取用户在组织架构中的ID
		url = '/bk/perm/del/list/rolesUser/?search_key=&page=1&page_size=100'
		res = self.send_request('get', url, headers)
		response = list(filter(lambda x: x['name'] == phone, res.json()['data']['data_list']))[0]
		return response['id']

	def get_role_id(self, headers):
		# 获取功能角色ID
		url = f'/bk/perm/roles/add/?type=function'
		res = self.send_request('get', url, headers)
		add_role_id = res.json()['data']['id']
		return add_role_id

	def get_roles_id(self, headers):
		# 搜索自己创建的功能角色
		url = '/bk/perm/del/list/roles/?type=function&search_key=&page=1&page_size=100'
		res = self.send_request('get', url, headers)
		response = list(filter(lambda x: '宋昌明' in x['name'], res.json()['data']))
		if response:
			return response[0]['id']

	def add_role_lists(self, headers, add_role_id, username):
		# 创建包含所有权限的功能角色
		url = f'/bk/perm/roles/retrieve/{add_role_id}/'
		if username == 'hualifang':
			body = {'name': ['权限管理-宋昌明' + str(add_role_id)],
					'csrfmiddlewaretoken': [headers['csrftoken']], 'choice_id_list': [
					'[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,52,53,54,56,57,58,60,61,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,141,142,143,144,145,146,147,148,149,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,200,201,202,203,209,210,211,212,213,214,215,216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,236,237,238,239,240,241,242,338,339,340,341,342,343,344,345,346,347,348,349,350,351,352,353]'],
					'leibie': ['功能']}
		elif username == 'huayuansu':
			body = {'name': ['权限管理-宋昌明' + str(add_role_id)],
					'csrfmiddlewaretoken': [headers['csrftoken']], 'choice_id_list': [
					'[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,97,98,99,100,101,104,105,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,200,201,202,203,209,210,211,212,213,214,215,216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,236,237,238,239,240,241,242,243,244,245,246,250,251,252,253,254,255,256,257,258,259,260,261,262,263,264,265,266,267,268,269,270,271,272,273,274,275,276,277,278,279,280,281,282,283,284,285,286,287,288,289,290,291,292,293,294,295,296,297,298,299,300,301,302,303,304,305,306,307,308,309,310,311,312,313,314,315,316,317,318,319,320,321,322,323,324,325,326,327,328,329,330,331,332,333,334,335,336,337,338,339,340,341,342,343,344,345,346,347,348,349,350,351,352,353,354,355,356,357,358,359,360,361,362,363,364,365,366,367,368,369,370,371,372]'],
					'leibie': ['功能']}
		res = self.send_request('post', url, headers, params=body)

	def give_roles_to_users(self, headers, user_id, role_type, username, role_id=None):
		# 获取权限管理模式
		url = f'/bk/perm/edit/roleUser/{user_id}/'
		if role_type == '单人模式':
			body = {'csrfmiddlewaretoken': [headers['csrftoken']]}
			res = self.send_request('post', url, headers, params=body)
		elif role_type == '分权模式':
			body_1 = {'select': ['1'], 'csrfmiddlewaretoken': [headers['csrftoken']]}
			body_2 = {'select': ['2'], 'csrfmiddlewaretoken': [headers['csrftoken']]}
			res = self.send_request('post', url, headers, params=body_1)
			res = self.send_request('post', url, headers, params=body_2)
		elif role_type == '管控模式' and username == 'huayuansu':
			body = {'role_list': [str(role_id)], 'csrfmiddlewaretoken': [headers['csrftoken']]}
			res = self.send_request('post', url, headers, params=body)
		elif role_type == '管控模式' and username == 'hualifang':
			body = {'role_list': [str(role_id)], 'csrfmiddlewaretoken': [headers['csrftoken']]}
			res = self.send_request('post', url, headers, params=body)

	def swith_to_company(self, headers, company_information):
		# 进行公司切换
		url = '/channel/business/switch_company/'
		body = {'com_id': company_information.get('company_id', '')}
		res = self.send_request('post', url, headers, params=body)

	def get_shop_url(self, headers, name=None):
		# 获取商铺地址
		url = '/bk/shop/search/?page=1&pagesize=30'
		res = self.send_request('get', url, headers)
		if not name:
			name = '诺贝尔'
		response = list(filter(lambda x: name in x['title'], res.json()['data']['results']))[0]
		return {'shopid': response['shopid'], 'brand_id': response['brand_id']}

	def personal_shop(self, headers, shop_url, sale_id=None):
		# 登录华世界商圈，获取商品清单
		shopid = shop_url['shopid']
		brandid = shop_url['brandid']
		url = f'/bk/personal_shop/{shopid}/?brandid={brandid}'
		res = self.send_request('get', url, headers)
		if sale_id:
			response = list(filter(lambda x: sale_id['sale_id_1'] == x['id'] or sale_id['sale_id_2'] == x['id'],
								   res.json()['data']['forsales']))
			product_id = {'product_id_1': response[0], 'product_id_2': response[1]}
		else:
			sale_id_1 = jsonpath(res.json(), '$.data.forsales[0].id')
			sale_id_2 = jsonpath(res.json(), '$.data.forsales[1].id')
			product_id = {'product_id_1': sale_id_1[0], 'product_id_2': sale_id_2[0]}
		return product_id

	def add_batch_to_cart(self, headers, sale_id):
		# 通过商品详情添加商品到购物车
		url = f'/orderinfo/api/addSaleToCart/'
		body_1 = {'sale_id': [sale_id['product_id_1']], 'num': [10], 'format': ['json']}
		body_2 = {'sale_id': [sale_id['product_id_2']], 'num': [10], 'format': ['json']}
		res = self.send_request('post', url, headers, params=body_1)
		res = self.send_request('post', url, headers, params=body_2)

	def addSaleToCart(self, headers, num, sale_id):
		# 通过华世界店添加商品到购物车
		url = f'/orderinfo/api/addSaleToCart/?meta=3'
		body_1 = {'num': [num], 'csrfmiddlewaretoken': [headers['csrftoken']],
				  'sale_id': [sale_id['product_id_1']]}
		body_2 = {'num': [num], 'csrfmiddlewaretoken': [headers['csrftoken']],
				  'sale_id': [sale_id['product_id_2']]}
		res = self.send_request('post', url, headers, params=body_1)
		res = self.send_request('post', url, headers, params=body_2)

	def sale_list(self, headers, sale_id):
		'''获取购物车清单'''
		url = f'/orderinfo/themeapp/cart/list/'
		res = self.send_request('get', url, headers)
		result = res.json()['data']['snap_list']
		group_list=list(filter(lambda x: '诺贝尔' in x['com_name'],result ))[0]['group_list']
		response = list(
			filter(lambda x: x['sale_id'] == sale_id['product_id_1'] or x['sale_id'] == sale_id['product_id_2'],
				   group_list))
		return {'product_id_1': response[0]['id'], 'product_id_2': response[1]['id']}

	def updateSaleCartNum(self, headers, snap_id):
		# 更新购物车中购买商品数量
		url = f'/orderinfo/api/updateSaleCartNum/'
		body_1 = {'snap_id': json.dumps(snap_id['product_id_1']), 'num': 100}
		body_2 = {'snap_id': json.dumps(snap_id['product_id_2']), 'num': 100}
		res = self.send_request('post', url, headers, params=body_1)
		res = self.send_request('post', url, headers, params=body_2)

	def get_address(self, headers):
		# 获取收货地址ID
		url = f'/bk/addr/conf/new/'
		res = self.send_request('get', url, headers)
		address_id = res.json()['data']['object_list'][0]['id']
		return address_id

	def add_address(self, headers):
		# 新增收货地址
		url = f'/bk/addr/addnew/'
		body = {'id': [''],
				'nick_title': [''],
				'shenFen': ['北京'],
				'chenShi': ['北京'],
				'quxian': ['西城区'],
				'diZhi': ['测试地址007'],
				'lianXiRen': ['测试007'],
				'dianHua': ['13511111111'],
				'tag': [''],
				'moren': ['false']}
		res = self.send_request('post', url, headers, params=body)
		address_id = res.json()['data']['id']
		return address_id

	def get_payrate(self, headers, list_ids):
		# 获取付款比例ID
		url = f"/orderinfo/rate/new_list/?key=&page=1&pagesize=100"
		response = self.send_request("get", url, headers)
		res = list(filter(lambda x: x['pay_rate'] == list_ids, response.json()["data"]["payrate_list"]))[0]
		return res['id']

	def add_payrate(self, headers, list_ids):
		# 新增付款比例
		url = f"/orderinfo/rate/base/0/"
		names = datetime.datetime.today().strftime("%m%d%H%M")
		params = {"name": f"付款比例{names}",
				  "isdefault": 1,
				  "prepayPercent": list_ids[0],
				  "deliveryPercent": list_ids[1],
				  "arrivalPercent": list_ids[2],
				  "installPercent": list_ids[3],
				  "finishPercent": list_ids[4],
				  "warrantyPercent": list_ids[5],
				  "deliveryPercentDay": list_ids[1],
				  "arrivalPercentDay": list_ids[2],
				  "installPercentDay": list_ids[3],
				  "warrantyPercentDay": list_ids[5],
				  "shelf_life": list_ids[5],
				  "deliveryPercentType": "work",
				  "arrivalPercentType": "work",
				  "installPercentType": "work",
				  "warrantyPercentType": "work",
				  "op": "create"}
		response = self.send_request("post", url, headers, params=params)
		return response.json()['data']['id']

	def delete_payrate(self,headers,payrate_id):
		# 删除付款比例
		url = f'/orderinfo/rate/base/{payrate_id}/'
		body = {'op': 'delete'}
		res = self.send_request('post', url, headers, params=body)

	def creat_order(self, headers, list_id):
		# 获取订单ID
		url = f'/orderinfo/themeapp/create/order/'
		body = {'ids': [list_id['product_id_1'], list_id['product_id_2']]}
		res = self.send_request('post', url, headers, params=body)

	def cartorderpost(self, headers, list_id, address_id):
		# 提交订单，获取订单ID
		url = f'/orderinfo/api/cartorderpost/'
		body1 = {"snap_id": list_id['product_id_1'], "msg": ""}
		body2 = {"snap_id": list_id['product_id_2'], "msg": ""}
		body = {'dizhi_id': address_id, 'songdashijian': '', 'distribu_mode': 'Merchant_distri',
				'shigong_danwei': '222', 'gongcheng_mingcheng': '111',
				'ids': [json.dumps(body1), json.dumps(body2)],
				'dingdanchaifen': [], 'msg': '', 'wuliu': '', 'total_order_flag': 'false'}
		res = self.send_request('post', url, headers, params=body)
		order_information = {'order_id': res.json()['data']['id'], 'pay_id': res.json()['data']['pay_id']}
		return order_information

	def orderdetails(self, headers, order_id):
		# 查询订单信息，获取预付款金额信息
		url = f'/orderinfo/v2/orderdetails/?origin=normal&order_type=new&pk={order_id}'
		res = self.send_request('get', url, headers)
		order_information = {'amount': res.json()['data']['settle_amount'],
							 'pay_rate': res.json()['data']['pay_rate']['pay_rate']}
		return order_information

	def new_order(self, headers, old_order):
		# 获取关联订单ID
		url = f'/orderinfo/order/related/orders/drf/{old_order}/'
		res = self.send_request('get', url, headers)
		new_order_id = res.json()['data']['intimate'][0]['id']
		return new_order_id

	def get_detail(self, headers, order_id):
		# 通过财务管理查询对应订单的信息
		url = f'/bk/financial/pay/info/detail/?pay_id={order_id}'
		res = self.send_request('get', url, headers)

	def orderdetail_information(self, headers, order_id, order_condition):
		# 通过查询条件查询订单信息
		url = f'/orderinfo/v2/orderdetails/?origin=normal&pk={order_id}&order_type=new'
		res = self.send_request('get', url, headers)
		result = res.json()
		if order_condition == '分单商品信息':
			snap_list = jsonpath(result, '$.data.snap_list')
			snap_details = [{"num": snap_list[0][0]['num'], "price": snap_list[0][0]['price'],
							 "snap_parent_id": snap_list[0][0]['id']},
							{"num": snap_list[0][1]['num'], "price": snap_list[0][1]['price'],
							 "snap_parent_id": snap_list[0][1]['id']}]
			return snap_details
		elif order_condition == '关联订单':
			rate_information = jsonpath(result, '$.data.shoukuan_pay_list')
			pay_rate = jsonpath(result, '$.data.pay_rate.pay_rate')
			order_no = jsonpath(result, '$.data.order_no')
			rate_amount = {'pay_rate': pay_rate[0], 'curr_id': order_id, 'order_no': order_no[0]}
			for i in rate_information[0]:
				curr_pay_id = i['id']
				amount = i['amount']
				title = i['title']
				rate_amount[title] = {'curr_pay_id': curr_pay_id, 'amount': amount}
			return rate_amount
		elif order_condition == '发货分批':
			rate_information = jsonpath(result, '$.data.shoukuan_pay_list')
			response = list(filter(lambda x: x['title'] == '发货款', rate_information[0]))[0]
			goods_batch = {
				'batch_1': {'curr_pay_id': response['batchs'][0]['id'], 'amount': response['batchs'][0]['amount']},
				'batch_2': {'curr_pay_id': response['batchs'][1]['id'], 'amount': response['batchs'][1]['amount']}}
			return goods_batch
		elif order_condition == '到货分批':
			rate_information = jsonpath(result, '$.data.shoukuan_pay_list')
			response = list(filter(lambda x: x['title'] == '到货款', rate_information[0]))[0]
			goods_batch = {
				'batch_1': {'curr_pay_id': response['batchs'][0]['id'], 'amount': response['batchs'][0]['amount']},
				'batch_2': {'curr_pay_id': response['batchs'][1]['id'], 'amount': response['batchs'][1]['amount']}}
			return goods_batch
		elif order_condition == 'all':
			return result

	def fukuan_pay(self, headers, pay_id, files):
		# 线下支付
		url = '/channel/v2/offline/pay/'
		body = {'pk': [str(pay_id)], 'payNo': ['123']}
		res = self.send_request('post', url, headers, params=body, files=files)

	def balance_pay(self, headers, pay_id, amount):
		# 余额支付
		url = f'/channel/v2/cash/pay/'
		body = {'bill_amount': [''], 'bill_img': [''], 'payId': [''], 'payImg': [''], 'pk': [str(pay_id)],
				'pay_amount': [str(amount)], 'ifquane': ['quane']}
		res = self.send_request('post', url, headers, params=body)
		if res.json()['errcode'] != 0:
			return res

	def get_now_use_mysql(self, headers):
		url = f'/orderinfo/v2/orderlist/'
		response = self.send_request('get', url, headers)
		one_order = response.json()['data']['order_list'][2]['order_no']

		datadb = Operation_mysql()
		host = '192.168.188.12'
		db = ''
		sql_data_1 = "show databases"
		sql_data_2 = f"SELECT * FROM order_orderinfo where assist_order='{one_order}'"
		names = datadb.get_information(sql_data_1, host, db)
		first_names = list(filter(lambda x: 'epodb_2020' in x, names))
		for mysql_name in first_names:
			try:
				values = datadb.get_information(sql_data_2, host, mysql_name, 1)
			except:
				values = None
			if values:
				print(mysql_name)
				break
		else:
			for mysql_name in names:
				try:
					values = datadb.get_information(sql_data_2, host, mysql_name, 1)
				except:
					values = None
				if values:
					return mysql_name
				else:
					print('未找到该订单数据')

	def find_if_all_cash(self, pay_id):
		datadb = Operation_mysql()
		host = '192.168.188.12'
		db = 'epodb_20200928'
		sql_data = f"SELECT if_all_cash FROM order_pay where id ='{pay_id}'"
		names = datadb.get_information(sql_data, host, db)
		return names[0]

	def shoukuan_pay(self, headers, order_information, amount,conditon):
		# 收款
		url = '/orderinfo/v2/comnfirm/pay/'
		if conditon:
			body = {'pay_id': order_information, 'shishou_jine': 0}
		else:
			body = {'pay_id': order_information, 'shishou_jine': amount}
		res = self.send_request('post', url, headers, params=body)

	def split_order(self, headers, order_id, snap_details, pay_rate_id, condition=0):
		# 操作订单分单,0:分单给商户；1：分单给华元素；2：不通过华元素（特殊战采）
		url = f'/orderinfo/split/order/{order_id}/?auto_split=1&degree=1'
		if condition in [1,2]:
			snap_details_new = [{"price": snap_details[0]['price'] - 2, "num": snap_details[0]['num'],
								 "snap_parent_id": snap_details[0]['snap_parent_id'],
								 "hys_purchase_price": snap_details[0]['price'] - 3},
								{"price": snap_details[1]['price'] - 2, "num": snap_details[1]['num'],
								 "snap_parent_id": snap_details[1]['snap_parent_id'],
								 "hys_purchase_price": snap_details[1]['price'] - 3}]
			body1 = '[{"com_id":"153","com":"","degree":"1","pay_rate_id": %s,"hys_pay_rate_id":%s,"snap_details":%s}]' % (
				pay_rate_id[0], pay_rate_id[1], json.dumps(snap_details_new))
			body = {'degree': ['1'], 'split_details': [body1],
					'csrfmiddlewaretoken': [headers['csrftoken']]}
			if condition==2:
				url = f'/orderinfo/split/order/{order_id}/?auto_split=0&degree=1'

		elif condition==0:
			body1 = '[{"com_id":34,"com":"华元素采购（深圳）有限公司","degree":"1","pay_rate_id":%s,"snap_details":%s}]' % (
				pay_rate_id[2], json.dumps(snap_details))
			body = {'degree': ['1'], 'split_details': [body1],
					'csrfmiddlewaretoken': [headers['csrftoken']]}
		else:
			return False

		res = self.send_request('post', url, headers, params=body)

	def active_order(self, headers, order_id):
		# 接单
		url = f'/orderinfo/api/confirm/order/?pk={order_id}'
		res = self.send_request('get', url, headers)

	def prepare_goods(self, headers, order_id):
		# 备货
		url = '/orderinfo/v2/prepare/goods/'
		body = {'pk': [str(order_id)], 'csrfmiddlewaretoken': headers['csrftoken']}
		res = self.send_request('post', url, headers, params=body)

	def split_snap_id(self, headers, order_id, condition):
		# 获取分批发货商品快照ID
		url = f'/orderinfo/themeapp/shipping/batch/list/v3/{order_id}/?type=add&id={order_id}&is_zhancai=true&order_type=new'
		response = self.send_request('get', url, headers)
		if condition == '分批':
			goods_snapid_1 = jsonpath(response.json(), '$.data.data.order_snap_list[0].id')
			goods_snapid_2 = jsonpath(response.json(), '$.data.data.order_snap_list[1].id')
			return {'goods_snapid_1': goods_snapid_1[0], 'goods_snapid_2': goods_snapid_2[0]}
		elif condition == '发货':
			goods_snapid_1 = jsonpath(response.json(), '$.data.data.order_snap_list[0].id')
			goods_snapid_2 = jsonpath(response.json(), '$.data.data.order_snap_list[1].id')
			batches_list_1 = jsonpath(response.json(), '$.data.data.batches_list[0].id')
			num_1 = jsonpath(response.json(), '$.data.data.batches_list[0].snaps[0].num')
			batches_list_2 = jsonpath(response.json(), '$.data.data.batches_list[1].id')
			num_2 = jsonpath(response.json(), '$.data.data.batches_list[1].snaps[0].num')
			return {'batches_list_1': {'id': batches_list_1[0], 'num': num_1[0],
									   'goods_snapid_1': goods_snapid_1[0], 'goods_snapid_2': goods_snapid_2[0]},
					'batches_list_2': {'id': batches_list_2[0], 'num': num_2[0],
									   'goods_snapid_1': goods_snapid_1[0], 'goods_snapid_2': goods_snapid_2[0]}}

	def split_goods(self, headers, order_id, snap_ids):
		# 货物分为2个批次
		url = f'/orderinfo/batch/shipping_batch_add/{order_id}/'
		get_datatime_1 = (datetime.datetime.today() + datetime.timedelta(1)).strftime("%Y-%m-%d")
		get_datatime_2 = (datetime.datetime.today() + datetime.timedelta(5)).strftime("%Y-%m-%d")
		names_1 = {"comments": "", "date": get_datatime_1,
				   "snap_nums": [{"snap_id": str(snap_ids['goods_snapid_1']), "num": "40"},
								 {"snap_id": str(snap_ids['goods_snapid_2']), "num": "40"}]}
		names_2 = {"comments": "", "date": get_datatime_2,
				   "snap_nums": [{"snap_id": str(snap_ids['goods_snapid_1']), "num": "60"},
								 {"snap_id": str(snap_ids['goods_snapid_2']), "num": "60"}]}
		body_1 = {'batch': json.dumps(names_1)}
		body_2 = {'batch': json.dumps(names_2)}
		response = self.send_request('post', url, headers, params=body_1)
		response = self.send_request('post', url, headers, params=body_2)

	def get_batch_goods_1(self, headers, snap_ids):
		batch_id = snap_ids.get('id', '')
		url = f'/orderinfo/themeapp/batch/delivery/v3/{batch_id}/'
		response = self.send_request('get', url, headers)

	def right_batch_goods(self, headers, snap_ids):
		# 确认分批发货信息
		batch_id = snap_ids.get('id', '')
		deliver_time = int(time.time())
		receive_num_1 = 'receive_num' + str(snap_ids.get('goods_snapid_1', ''))
		receive_num_2 = 'receive_num' + str(snap_ids.get('goods_snapid_2', ''))
		url = f'/orderinfo/themeapp/batch/delivery/v3/{batch_id}/'
		body = {'deliver_time': deliver_time, receive_num_1: snap_ids.get('num', ''),
				receive_num_2: snap_ids.get('num', '')}
		response = self.send_request('post', url, headers, params=body)

	def get_batch_goods_2(self, headers, snap_ids):
		batch_id = snap_ids.get('id', '')
		url = f'/orderinfo/themeapp/batch/delivery/second/v3/{batch_id}/'
		response = self.send_request('get', url, headers)

	def send_batch_goods(self, headers, order_id, snap_ids, files):
		# 分批发货
		batch_id = snap_ids.get('id', '')
		url = f'/orderinfo/api/delivery/goods/?batchid={batch_id}'
		body = {'fahuo_man': '123', 'fahuo_phone': '456', 'wayNo': '789', 'pk': str(order_id)}
		response = self.send_request('post', url, headers, params=body, files=files)

	def give_batch_goods_1(self, headers, order_id, snap_ids):
		# 批次到货验收1-1
		batch_id = snap_ids.get('id', '')
		url = f'/channel/v2/goods/check_step/?pk={order_id}&batch={batch_id}'
		response = self.send_request('get', url, headers)

	def give_batch_goods_2(self, headers, order_id, snap_ids):
		# 批次到货验收1-2
		batch_id = snap_ids.get('id', '')
		url = f'/channel/v2/goods/check_step/?pk={order_id}&batch={batch_id}&re_verify='
		response = self.send_request('get', url, headers)

	def check_batch_goods(self, headers, order_id, snap_ids):
		# 批次到货验收2
		batch_id = snap_ids.get('id', '')
		url = f'/channel/v2/goods/check/?batch={batch_id}&re_verify='
		time_now = time.time()
		body = {'pk': [str(order_id)], 'batch': [batch_id], 'msg': ['123'], 'result': ['合格'],
				'receive_time': ['%.2f' % (time_now * 1000)],
				'receive_num' + str(snap_ids['goods_snapid_1']): [snap_ids['num']],
				'receive_num' + str(snap_ids['goods_snapid_2']): [snap_ids['num']]}
		response = self.send_request('post', url, headers, params=body)

	def check_batch_start(self, headers, order_id, snap_ids, files):
		# 施工方到货验收
		batch_id = snap_ids.get('id', '')
		url = f'/channel/v2/goods/check/?batch={batch_id}'
		body = {'pk': order_id, 'batch': batch_id}
		response = self.send_request('post', url, headers, params=body, files=files)

	def check_batch_middle(self, headers, order_id, snap_ids):
		# 平台批次到货验收
		batch_id = snap_ids.get('id', '')
		url = f'/orderinfo/api/platform/goods/check/{order_id}/?batch={batch_id}'
		body = {'note': '123'}
		response = self.send_request('post', url, headers, params=body)

	def batch_goods_pay(self, headers, order_id):
		# 获取批次付款ID
		url = f'/orderinfo/themeapp/shipping/batch/list/v3/{order_id}/?type=detail&id={order_id}&is_zhancai=true&order_type=new'
		response = self.send_request('get', url, headers)
		pay_id_1 = jsonpath(response.json(), '$.data.data.batches_list[0].operate_list[0].app_data_params.pay_id')
		amount_1 = jsonpath(response.json(), '$.data.data.batches_list[0].amount')
		pay_id_2 = jsonpath(response.json(), '$.data.data.batches_list[1].operate_list[0].app_data_params.pay_id')
		amount_2 = jsonpath(response.json(), '$.data.data.batches_list[1].amount')
		return {'batches_list_1': {'pay_id': pay_id_1, 'amount': amount_1},
				'batches_list_2': {'pay_id': pay_id_2, 'amount': amount_2}}

	def get_goods_information(self, headers, order_id):
		# 获取到发货清单快照ID
		url = f'/channel/v2/delivery/goods/?pk= {order_id}'
		res = self.send_request('get', url, headers)
		return [res.json()['data']['snap_list'][0]['id'], res.json()['data']['snap_list'][1]['id']]

	def right_goods(self, headers, snap_id, order_id):
		# 确认发货信息
		url = '/channel/v2/delivery/goods/'
		body = {'pk': [str(order_id)], 'batchid': [''], 'receive_num' + str(snap_id[1]): [100],
				'receive_num' + str(snap_id[0]): [100]}
		res = self.send_request('post', url, headers, params=body)

	def delivery_goods(self, headers, order_id, files):
		# 厂家发货
		url = '/channel/v2/delivery/goods/'
		body = {'pk': [str(order_id)], 'batchid': [''], 'fahuo_man': ['123'], 'fahuo_phone': ['456'], 'wayNo': ['789']}
		res = self.send_request('post', url, headers, params=body, files=files)

	def ckeck_goods_information(self, headers, order_id):
		# 获取到验收清单信息快照ID
		url = f'/channel/v2/goods/check/?batch=&re_verify&pk={order_id}'
		res = self.send_request('get', url, headers)
		snap_id = [item['id'] for item in res.json()['data']['snap_list']]
		return snap_id

	def right_check_goods(self, headers, snap_id, order_id):
		# 确认到货验收1
		url = '/channel/v2/goods/check/?batch=&re_verify='
		time_now = time.time()
		body = {'pk': [str(order_id)], 'batch': [''], 'msg': ['123'], 'result': ['合格'],
				'receive_time': ['%.3f' % (time_now * 1000)], 'receive_num' + str(snap_id[0]): [100],
				'receive_num' + str(snap_id[1]): [100], 'csrfmiddlewaretoken': headers['csrftoken']}
		res = self.send_request('post', url, headers, params=body)

	def check_goods(self, headers, order_id, files, batch_id=None):
		# 确认到货验收2
		url = '/channel/v2/goods/check/?batch='
		body = {'pk': [str(order_id)], 'batch': [batch_id]}
		res = self.send_request('post', url, headers, params=body, files=files)

	def orderinfo_check_goods(self, headers, order_id):
		# 到场验收完毕
		url = f'/orderinfo/api/platform/goods/check/{order_id}/'
		body = {'note': ['123'], 'pk': [str(order_id)]}
		res = self.send_request('post', url, headers, params=body)

	def install_goods(self, headers, order_id, files):
		# 安装
		url = '/orderinfo/api/complete/install/'
		body = {'pk': [str(order_id)], 'batch': ['']}
		res = self.send_request('post', url, headers, params=body, files=files)

	def check_install(self, headers, order_id, files=None):
		# 安装验收
		url = '/orderinfo/api/install/check/'
		if files:
			body = {'pk': order_id, 'result': '', 'msg': ''}
		else:
			body = {'pk': order_id, 'note': '测试数据'}
		res = self.send_request('post', url, headers, params=body, files=files)

	def account_check(self, headers, order_id):
		url = '/orderinfo/v2/settle/account/check/'
		body = {'pk': order_id}
		res = self.send_request('post', url, headers, params=body)

	def complete_insurance(self, headers, order_id, files):
		# 质保结束
		url = '/orderinfo/api/complete/insurance/'
		body = {'pk': order_id}
		res = self.send_request('post', url, headers, params=body, files=files)

	def sign_in(self, num=0):
		# 注册新用户
		url = self.environment + '/channel/im/app_user_register/'
		if isinstance(num,int):
			phone_header = 134
			phone_num = str(time.strftime('%m%d%H%M', time.localtime(time.time())))
			body = {'phone': [str(phone_header + num) + phone_num], 'code': ['111111'], 'password': ['111111'],'confirmPassword': ['111111'], 'password1': ['111111'], 'agreeToDeal': ['true']}
		else:
			body = {'phone': [num], 'code': ['111111'], 'password': ['111111'],'confirmPassword': ['111111'], 'password1': ['111111'], 'agreeToDeal': ['true']}
		res = self.session.post(url, data=body)
		sign_information = {}
		if res.json()['errcode'] == 0:
			member_id = res.json()['data']['memberid']
			login_name = res.json()['data']['phone']
			sign_information = {'member_id': member_id, 'login_name': login_name}
			print('注册用户成功:', sign_information.get('login_name', ''))
		elif res.json()['errcode'] == 2:
			sign_information = {'login_name': body['phone'][0]}
			print('用户已注册:', sign_information.get('login_name', ''))
		return sign_information

	def add_application(self, headers, app_id):
		# 添加用户使用记录
		url_1 = f'/thirparty/app/application/record/add'
		body = {'application_id': app_id, 'type': 'func'}
		response1 = self.send_request('post', url_1, headers, params=body)

	def add_personal_company(self, headers):
		self.add_application(headers, 60)
		# 获取认证公司的ID
		url_2 = f'/personal/company_info/'
		response2 = self.send_request('get', url_2, headers)
		company_id = response2.json()['data']['com']['id']
		return company_id

	def company_name(self, headers, name, num):
		# 获取公司名称
		url = f'/personal/tianyan_search/?name={name}'
		res_url = quote(url, safe=";/?:@&=+$,", encoding="utf-8")  # 编码
		res = self.send_request('get', res_url, headers)
		company_names = res.json()['data'][num]
		return company_names

	def company_information(self, headers, name):
		# 获取公司信息
		url = f'/personal/tianyan_precise_search/?name={name}'
		res_url = quote(url, safe=";/?:@&=+$,", encoding="utf-8")  # 编码
		res = self.send_request('get', res_url, headers)
		return res.json()['data']

	def add_brands(self, headers, company_id, files):
		# 添加品牌
		url = f'/personal/platform/modify/company/brandlogoupload/'
		body = {'type': 'add', 'com_id': company_id, 'brandName': '东方'}
		response = self.send_request('post', url, headers, params=body, files=files)

	def company_prove(self, headers, company_information, files, condition):
		# 填写公司认证信息
		url = f'/personal/company_info/'
		if condition in ('生产商', '渠道商'):
			body = {'name': [company_information['name']], 'No': [company_information['taxNumber']],
					'address': [company_information['regLocation']],
					'linkman': [company_information['legalPersonName']],
					'phone': [company_information['phoneNumber']], 'shenFen': ['四川'], 'chenShi': ['成都'],
					'quxian': ['武侯区'], 'com_type': [company_information['companyOrgType']],
					'com_cate': [condition], 'taxplayer_type': ['0'], 'certification_type': ['法定代表人手持身份证'],
					'management': [company_information['businessScope']], 'leibie': ['produce'],
					'legal_person': ['yes'], 'product_licence_delete': ['false'],
					'logo_delete': ['false'], 'IdCard': [''], 'backIdCard': [''],
					'taxplayer_licence': [''], 'producter_licence': [''], 'brands': ['["东方"]'],
					'is_accept': ['accept']}
		else:
			body = {'name': [company_information['name']], 'No': [company_information['taxNumber']],
					'address': [company_information['regLocation']],
					'linkman': [company_information['legalPersonName']],
					'phone': [company_information['phoneNumber']], 'shenFen': ['四川'],
					'chenShi': ['成都'], 'quxian': ['武侯区'],
					'com_type': [company_information['companyOrgType']], 'com_cate': [condition],
					'taxplayer_type': ['0'], 'management': [company_information['businessScope']],
					'leibie': ['notProduce'], 'legal_person': ['yes'], 'certification_type': ['法定代表人手持身份证'],
					'product_licence_delete': ['false'], 'logo_delete': ['false'], 'IdCard': [''],
					'backIdCard': [''], 'logo': [''], 'taxplayer_licence': [''],
					'is_accept': ['accept']}
		res = self.send_request('post', url, headers, params=body, files=files)

	def company_prove_id(self, headers, company_information,conditon='pending'):
		# 获取公司的ID：pending为待审批，finish为已审批，dismissed为已驳回
		url = f'/personal/company/auth/list/v3/?type={conditon}&page=1&pageSize=100&key='
		res = self.send_request('get', url, headers)
		response=list(filter(lambda x:x['name'] == company_information['name'],res.json()['data']['com_list']))[0]
		return response['id']

	def compare_company_prove(self, headers, crm_company_id):
		# 通过公司认证
		url = f'/personal/company_auth_detail/?id={crm_company_id}'
		body = {'level': '', 'tag': '', 'op': 1}
		res = self.send_request('post', url, headers, params=body)

	def cash_list_id(self, headers, company_name):
		# 获取充值ID
		url = f'/bk/financial/cash/account/list/0/?page=1&pagesize=10&key={company_name}'
		res_url = quote(url, safe=";/?:@&=+$,", encoding="utf-8")  # 编码
		res = self.send_request('get', res_url, headers)
		cash_id = res.json()['data']['res_data'][0]['id']
		return cash_id

	def pay_cash_information(self, headers, cash_id):
		# 查询充值信息
		url = f'/bk/financial/recharge/pay/ing/{cash_id}/'
		res = self.send_request('get', url, headers)
		cash_information = {}
		cash_information['pay_final_com_id'] = res.json()['data']['pay_final_com_id']
		cash_information['pay_no'] = res.json()['data']['pay_no']
		return cash_information

	def pay_cash_to_up(self, headers, cash_information, cash_id, files):
		# 下游充值
		url = f'/bk/financial/recharge/pay/ing/{cash_id}/'
		body = {'pay_way': ['线下支付'], 'pay_id': ['测试充值'], 'pay_no': [cash_information['pay_no']],
				'pay_amount': [1000000], 'pay_final_com_id': [cash_information['pay_final_com_id']]}
		res = self.send_request('post', url, headers, params=body, files=files)

	def get_up_cash(self, headers, cash_information):
		# 上游获取充值ID
		url = f'/bk/financial/recharge/pay/list/0/?page=1&page_size=10&key='
		res = self.send_request('get', url, headers)
		response = list(filter(lambda x: x['payNo'] == cash_information['pay_no'], res.json()['data']['res_data']))[0]
		return response['id']

	def pay_up_cash(self, headers, pay_id):
		# 上游充值收款
		url = f'/bk/financial/recharge/pay/confirm/{pay_id}/'
		res = self.send_request('post', url, headers)

	def get_json_path(self, result, json_value):
		# 获取json的jsonpath
		try:
			list_paths = []
			json_name = jsonPath.get_path(result, '$', json_value)
			print(json_name[0])
		except:
			print('未获取到对于的jsonpath')

	def set_product_id(self, product_id):
		# 产品ID
		self.product_id = product_id

	def set_sale_id(self, sale_id):
		# 商品ID
		self.sale_id = sale_id

	"""简单上架（已下架）"""

	def goods_shelves(self, headers):
		# 新建商品
		url1 = "/bk/product_name/onsale/forsales/edit/create/?action=new"
		response1 = self.send_request("get", url1, headers)
		self.set_product_id(response1.json()["data"]["id"])

		# 商品类别
		url2 = f"/bk/product_name/onsale/forsales/edit/catelog/{self.product_id}"
		params2 = {"catelog_id": [1466, 621, 622]}
		response2 = self.send_request("post", url2, headers, params2)

		# /
		url = f"/bk/product_name/onsale/forsales/edit/main/simple/{self.product_id}?format=json"
		response = self.send_request("get", url, headers)

		# 获取商品品牌ID
		url3 = f"/bk/product_name/onsale/forsales/edit/brand/{self.product_id}"
		response3 = self.send_request("get", url3, headers)
		brand_id = response3.json()["data"][0]["id"]

		# 添加商品品牌
		url4 = f"/bk/product_name/onsale/forsales/edit/brand/{self.product_id}"
		params4 = {"brand": brand_id, "action": "choice"}
		response4 = self.send_request("post", url4, headers, params4)

		# 添加商品单位
		url6 = f"/bk/product_name/onsale/forsales/edit/unit/{self.product_id}"
		params6 = {"unit": "箱"}
		response6 = self.send_request("post", url6, headers, params6)

		# 选择商品标准
		url10 = f"/bk/product_name/onsale/forsales/edit/name/{self.product_id}"
		params10 = {"attribute_ids": [2649, 2654], "type": "spec", "action": "add"}
		response10 = self.send_request("post", url10, headers, params10)
		data = response10.json()["data"][0]
		sale_id_1 = data["id"]  # 875579
		template_id_1 = data["sale_template"]["id"]  # 161241
		data_1 = response10.json()["data"][1]
		sale_id_2 = data_1["id"]  # 875579
		template_id_2 = data_1["sale_template"]["id"]  # 161241

		# 设置商品零售价
		url11 = f"/bk/product_name/onsale/forsale/edit/info/{sale_id_2}"
		params11_1 = {"market_price": 200, "crs": "300*300", "action": "modify"}
		response11_1 = self.send_request("post", url11, headers, params11_1)
		url11 = f"/bk/product_name/onsale/forsale/edit/info/{sale_id_1}"
		params11_2 = {"market_price": 400, "crs": "600*600", "action": "modify"}
		response11_2 = self.send_request("post", url11, headers, params11_2)

		# 添加商品名称
		url5 = f"/bk/product_name/onsale/forsales/edit/name/{self.product_id}"
		params5 = {"attribute_ids": 2596, "type": "title", "action": "modify"}
		response5 = self.send_request("post", url5, headers, params5)

		# 添加商品图片
		url8 = f"/bk/product_name/onsale/forsales/edit/images/{self.product_id}"
		params8 = {"action": "add", "index": 0}
		response8 = self.send_request("post", url8, headers, params8, files=self.get_img("image"))

		# 添加商品详情图片
		url9 = f"/bk/product_name/onsale/forsales/edit/template/{template_id_1}"
		params9 = {"type": "image", "pro_id": self.product_id, "action": "add"}
		response9 = self.send_request("post", url9, headers, params9, files=self.get_img("image"))
		url21 = f"/bk/product_name/onsale/forsales/edit/template/{template_id_2}"
		params21 = {"type": "image", "pro_id": self.product_id, "action": "add"}
		response9 = self.send_request("post", url21, headers, params21, files=self.get_img("image"))

		# 添加最小销售单元
		url20 = f"/bk/product_name/onsale/forsales/edit/sku/{self.product_id}"
		params20 = {"sku": 10, "sku_unit": "箱"}
		response20 = self.send_request("post", url20, headers, params20)

		# 提交商品创建
		url15 = f"/bk/product_name/onsale/forsales/edit/submit/{self.product_id}"
		response15 = self.send_request("get", url15, headers)

		sale_id = {"sale_id": [sale_id_1, sale_id_2]}
		print("新增商品成功", sale_id)
		return sale_id

	def get_circle_list(self,headers):
		# 获取圈层价列表
		url_1 = f"/orderinfo/circle/circle_price_list/?status=&search_key=&page=1&pagesize=20"
		response = self.send_request("get", url_1, headers)
		return response

	def set_circle_price_id(self, circle_price_id):
		# 设置新建圈层价ID
		self.circle_price_id = circle_price_id

	def set_circle_price(self, headers, sale_id, scale, company_id, payrate_ids):  # 4237
		# 新建圈层价
		url_1 = f"/orderinfo/circle/link/create/0/?class=ordinary"
		response1 = self.send_request("get", url_1, headers)
		self.set_circle_price_id(response1.json()["data"]["id"])

		# 获取商品底价
		# url4=f"/orderinfo/circle/get_markup_sales/0/{self.circle_price_id}/?key=&page=1&pagesize=10&catelogtag_id="

		# 设置圈层价商品
		self.set_sale_circle_price(headers, sale_id[0], scale)
		self.set_sale_circle_price(headers, sale_id[1], scale)

		url3 = f"/orderinfo/circle/link/create/{self.circle_price_id}/"
		names = datetime.datetime.today().strftime("%m%d%H%M")
		params3 = {"name": f"测试圈层价{names}",
				   "payrate": payrate_ids,
				   "start_time": str(datetime.datetime.now())[:16],
				   "can_try_see": 0,
				   "try_see_valid_time": 72,
				   "to_all_people": 0,
				   "com_ids": company_id}
		response3 = self.send_request("post", url3, headers, params=params3)
		print("新增圈层价成功", self.circle_price_id)

	def choose_company(self, headers, company=None):
		if not company:
			return 34
		url = f"/orderinfo/api/circle/select_cooperate/"
		response1 = self.send_request("get", url, headers)
		data = response1.json()["data"]["com_info"]
		company_id = list(filter(lambda x: x["name"] == company, data))[0]["id"]
		return company_id

	def set_sale_circle_price(self, headers, sale_id, scale):
		# 设置圈层价商品
		url2 = f"/orderinfo/circle/batch_set_markup_price_sale/{self.circle_price_id}"
		sale_data = json.dumps([{"id": sale_id, "moq": 10, "scale": scale}])
		params2 = {"sale_data": sale_data}
		response2 = self.send_request("post", url2, headers, params=params2)
		if response2.json()['errcode'] == -1 and '调价后已经低于底价' in response2.json()['msg']:
			scale += 1
			self.set_sale_circle_price(headers, sale_id, scale)

	def set_c_id(self, c_id):
		self.c_id = c_id

	def approval_circle_price(self, headers):
		# 获取圈层ID
		url1 = "/orderinfo/circle/circle_price_approve_list/?type=1&search_key=&page=1&pagesize=20&status=&factory_id="
		response1 = self.send_request("get", url1, headers)
		data_list = response1.json()["data"]
		response = list(filter(lambda x: x["circle_id"] == self.circle_price_id, data_list))[0]
		prove_circle_id = response["id"]
		print("待审批的圈层价ID为：", prove_circle_id)

		# 审核圈层价通过
		url2 = f"/orderinfo/circle/circle_price_approve/{prove_circle_id}/?result=1"
		response2 = self.send_request("post", url2, headers)

	def batch_goods(self, headers, transport_id, catelog_id=622, price=200):
		# """获取当前登录公司ID"""
		# url_21=f'/bk/product_name/onsale/com/sales/?page=1&page_size=10'
		# body={'status':'sale_on','search_key':''}
		# response21=self.send_request('post',url_21,headers,params=body)
		# company_id=response21.json()['data']['company']['id']

		"""创建批量上架商品单ID"""
		url_1 = f"/bk/product_name/onsale/batch/edit/sales/create/"
		params1 = {"action": "get"}
		response1 = self.send_request("post", url_1, headers, params=params1)
		goods_id = response1.json()["data"]["id"]

		# """获取行业分类"""
		# url_16 = f'/bk/setting/catelog/tree/'
		# response16 = self.send_request('post', url_16, headers)

		"""获取公司品牌"""
		url_21 = f'/bk/product_name/onsale/batch/edit/sales/brand/{goods_id}'
		response21 = self.send_request('get', url_21, headers)
		brand_id = response21.json()['data']['brands_dict'][0]['id']

		"""设置商品品类"""
		url_3 = f"/bk/product_name/onsale/batch/edit/sales/catelog/{goods_id}"
		params3 = {"catelog_id": catelog_id}
		response3 = self.send_request("post", url_3, headers, params=params3)

		"""设置商品品牌"""
		url_2 = f"/bk/product_name/onsale/batch/edit/sales/brand/{goods_id}"
		params2 = {"brand_id": brand_id}
		response2 = self.send_request("post", url_2, headers, params=params2)

		"""获取品类"""
		url_22 = f'/bk/product_name/onsale/metas/{catelog_id}'
		response22 = self.send_request('get', url_22, headers)
		name_list = response22.json()['data']['name_list'][0]['detail_list'][0]['detail_id']
		spec_list_1 = response22.json()['data']['spec_list'][0]['detail_list'][0]['detail_id']
		spec_list_2 = response22.json()['data']['spec_list'][0]['detail_list'][1]['detail_id']
		spec_list_3 = response22.json()['data']['spec_list'][0]['detail_list'][2]['detail_id']
		spec_list_4 = response22.json()['data']['spec_list'][0]['detail_list'][3]['detail_id']

		"""批量设置商品"""
		url_4 = f"/bk/product_name/onsale/batch/edit/sales/name/{goods_id}"
		params4 = {"meta_ids": [int(name_list), int(spec_list_1), int(spec_list_2), int(spec_list_3), int(spec_list_4)]}
		response4 = self.send_request("post", url_4, headers, params=params4)
		time.sleep(3)

		"""获取商品ID"""
		url_5 = f"/bk/product_name/onsale/batch/edit/sales/filter/{goods_id}?page_size=1&page=1"
		params5 = {"action": "filter", "catelog_id": catelog_id}
		response5 = self.send_request("post", url_5, headers, params=params5)
		sale_id_1 = jsonpath(response5.json(), "$.data.sale_list[0].children[0].id")
		sale_id_2 = jsonpath(response5.json(), "$.data.sale_list[0].children[1].id")
		sale_id_3 = jsonpath(response5.json(), "$.data.sale_list[0].children[2].id")
		sale_id_4 = jsonpath(response5.json(), "$.data.sale_list[0].children[3].id")
		sale_ids = [sale_id_1[0], sale_id_2[0], sale_id_3[0], sale_id_4[0]]

		"""设置商品价格"""
		url_7 = f"/bk/product_name/onsale/batch/edit/sales/price/{goods_id}"
		params7 = {"action": "modify", "price": price, "sale_ids": sale_ids[0]}
		response7 = self.send_request("post", url_7, headers, params=params7)
		url_8 = f"/bk/product_name/onsale/batch/edit/sales/price/{goods_id}"
		params8 = {"action": "modify", "price": price + 200, "sale_ids": sale_ids[1]}
		response8 = self.send_request("post", url_8, headers, params=params8)
		url_9 = f"/bk/product_name/onsale/batch/edit/sales/price/{goods_id}"
		params9 = {"action": "modify", "price": price + 400, "sale_ids": sale_ids[2]}
		response7 = self.send_request("post", url_9, headers, params=params9)
		url_10 = f"/bk/product_name/onsale/batch/edit/sales/price/{goods_id}"
		params10 = {"action": "modify", "price": price + 600, "sale_ids": sale_ids[3]}
		response10 = self.send_request("post", url_10, headers, params=params10)

		"""获取商品单位"""
		url_23 = f'/bk/product_name/onsale/batch/edit/sales/unit/{goods_id}'
		response23 = self.send_request('get', url_23, headers)
		unit_info = response23.json()['data']['units_info'][0]

		"""设置商品单位"""
		url_11 = f"/bk/product_name/onsale/batch/edit/sales/unit/{goods_id}"
		params11 = {"action": "modify", "set_type": "consistent", "unit": unit_info}
		response11 = self.send_request("post", url_11, headers, params=params11)

		"""设置商品最小销售单元"""
		url_12 = f"/bk/product_name/onsale/batch/edit/sales/skumoq/{goods_id}"
		params12 = {"action": "modify", "moq": "", "moq_unit": "", "sku": 10, "sku_unit": ""}
		response12 = self.send_request("post", url_12, headers, params=params12)

		"""设置运费模板"""
		url_13 = f"/bk/product_name/onsale/batch/edit/sales/transport/{goods_id}?page_size=1&page=1"
		params13 = {"action": "modify", "transport_id": transport_id}
		response13 = self.send_request("post", url_13, headers, params13)
		time.sleep(1)

		"""提交设置好的运费模板"""
		url_14 = f"/bk/product_name/onsale/batch/edit/sales/check/{goods_id}"
		params14 = {"check_type": "transport"}
		response14 = self.send_request("post", url_14, headers, params=params14)
		time.sleep(1)

		"""查看商品"""
		url_20 = f'/bk/product_name/onsale/batch/edit/sales/images/{goods_id}?page_size=1&page=1'
		body = {'action': 'filter'}
		response20 = self.send_request('post', url_20, headers, params=body)
		time.sleep(2)

		"""批量添加商品图片"""
		url_15 = f"/bk/product_name/onsale/batch/edit/sales/images/{goods_id}"
		params15 = {'action': 'add'}
		dicks = ['image']
		files = self.get_img(dicks)
		response15 = self.send_request('post', url_15, headers, params=params15, files=files)
		time.sleep(3)

		"""提交商品图片"""
		url_16 = f'/bk/product_name/onsale/batch/edit/sales/images/{goods_id}?page_size=1&page=1'
		params16 = {'action': 'filter'}
		response16 = self.send_request('post', url_16, headers, params=params16)
		time.sleep(1)

		"""获取商品详情模板ID"""
		url_17 = f'/bk/product_name/onsale/sale/template/details/list/622'
		response17 = self.send_request('get', url_17, headers)
		template_id = response17.json()['data'][0]['id']

		"""添加商品详情模板"""
		url_18 = f'/bk/product_name/onsale/batch/edit/sales/desc/{goods_id}'
		params18 = {'action': 'add', 'template_id': template_id}
		response18 = self.send_request('post', url_18, headers, params=params18)
		time.sleep(3)

		"""提交商品详情模板"""
		url_19 = f'/bk/product_name/onsale/batch/edit/sales/check/{goods_id}'
		params19 = {'check_type': 'final_check'}
		response19 = self.send_request('post', url_19, headers, params19)

		sale_id = {"sale_id": [sale_id_1[0], sale_id_2[0], sale_id_3[0], sale_id_4[0]]}
		print(sale_id)
		return sale_id

	def create_transport(self, headers):
		"""创建运费模板"""
		url_14 = f"/bk/new/transport/detail/?type=add&pk=undefined"
		template = {"template_name": "测试运费模板", "free_fee": True, "is_active": True, "non_deliver_city": ["海外"]}
		params14 = {'data_str': json.dumps(template)}
		response14 = self.send_request("post", url_14, headers, params=params14)

		transport_template_id = self.get_transports(headers)
		return transport_template_id

	def get_transports(self, headers):
		"""获取运费模板ID"""
		url_13 = f"/bk/product_name/onsale/com/transports/"
		res = self.send_request("get", url_13, headers)
		response = list(filter(lambda x: "测试运费模板" in x["name"], res.json()["data"]))[0]["transport_template_id"]
		return response

	def get_topic_id(self,headers):
		"""获取话题ID"""
		url=f'/subject/topic/list?pagesize=100&type=3'
		response=self.send_request('get',url,headers)
		topic_id=response.json()['data'][0]['id']
		return topic_id

	def public_trend(self,headers,topic_id,words):
		"""快速发帖"""
		url=f'/subject/trend/add'
		body={'topic_id':topic_id,'content':words,'type':1,'source':2,'video':None}
		response=self.send_request('post',url,headers,params=body)

	def im_push_message(self, member_id):
		host = 'http://192.168.188.12:3111'
		url = f"{host}/goim/push/members?operation=4"
		mids = str(member_id)
		# mids = mids.replace("[", "").replace("]", "")
		data ={'mids': '', 'message': '{"chatSession_id": 576, "msgType": 29, "msg": {"func": 1, "pk": "9207", "url": "/orderinfo/themeapp/order/details/?pk=9207&type=sellOrder", "data": [{"name": "\\u63cf\\u8ff0", "value": "\\u60a8\\u6709\\u4e00\\u4e2a\\u65b0\\u7684\\u8ba2\\u5355\\uff0c\\u8bf7\\u53ca\\u65f6\\u8ddf\\u8fdb\\u3002", "type": "desc", "order": 2}, {"name": "\\u8ba2\\u5355\\u91d1\\u989d", "value": "\\u00a52,259.22", "type": "price", "order": 3, "color": "#f7394e", "weight": "bold"}, {"name": "\\u4e0b\\u5355\\u7528\\u6237", "value": "\\u6cb3\\u5357\\u5e73\\u5b89\\u5b9e\\u4e1a\\u6709\\u9650\\u516c\\u53f8", "type": "string", "order": 4}, {"name": "\\u8ba2\\u5355\\u7f16\\u53f7", "value": "SZ06V78ALEWM", "type": "string", "order": 5}], "title": "\\u4e0b\\u5355\\u901a\\u77e5", "func_name": "\\u8ba2\\u5355\\u7ba1\\u7406", "icon": "", "button": []}, "fromUserid": 1318}'}

		try:
			response = requests.post(url, json=json.dumps(data))
			print(response.status_code)
			data = response.text
			print(data)
		except:
			print(111)

	def push_message_tomember(self,headers,member_ids,sender):
		# 推送消息给成员
		url=f'/channel/announcement/test/m2m/'
		body={'sender':sender,'receiver':member_ids}
		response=self.send_request('post',url,headers,params=body,status=11)
		# time.sleep(1)

	def push_message_togroup(self,headers,sender,member_ids):
		# 推送消息给群聊
		url=f'/channel/announcement/test/m2g/'
		body={'sender':sender,'group':[27123]}
		response=self.send_request('post',url,headers,params=body,status=11)

	def personal_message(self,headers):
		# 获取成员与小助手之间的session_id
		url=f'/personal/messages/'
		response=self.send_request('get',url,headers)
		session_id=list(filter(lambda x: x.get('memberid','')==1318,response.json()['data']))
		return session_id[0]['id']

	def chioce_type(self,headers):
		# 注册用户之后，加入行业
		url=f'/personal/personal_card/'
		body={'industry_id': 1440, 'is_register': 1}
		response=self.send_request('post',url,headers,params=body)

	def like_toggle(self,headers,trend_id):
		# 动态点赞
		url=f'/subject/trend/like/toggle'
		body={'trend_id': '2223','operate': '0'}
		response=self.send_request('post',url,headers,params=body)

	def add_draw(self,headers):
		# 添加抽奖
		url=f'/channel/activity/draw_add/5/'
		body={'csrfmiddlewaretoken': ['NWUYvwTTph7BeaUplkSWRjdYG5csFLb1j84p8NwOqWlrN6JquLa4tqAnBaKV3wCM'], 'id': [''], 'title': ['抽奖28'], 'draw_type': ['常规抽奖'], 'lottery_id': ['4'], 'count': ['3'], 'startTime': ['2020-10-29 19:55'], 'draw_count': ['1'], 'lottery_draw_id': ['']}
		response=self.send_request('post',url,headers,params=body)

	def get_draw_member(self,headers,draw_id):
		# 获取获奖名单
		url=f'/channel/activity/get_draw_member/?pk={draw_id}'
		response=self.send_request('get',url,headers)

	def get_orderstatu(self,headers,order_id):
		# 获取订单流转状态
		url=f'/orderinfo/api/orderstatusshow/?pk={order_id}'
		response=self.send_request('get',url,headers)

	def group_file_upload(self,headers,session_id):
		# 上传群文件
		url=f'/baseapi/wps/file/upload/'
		body={'session_id': session_id}
		files = [('file', open(f'D:/测试资料/APP-log.txt', 'rb'))]
		response=self.send_request('post',url,headers,params=body,files=files)

	def group_file_list(self,headers,session_id):
		# 获取群文件清单
		url=f'/baseapi/group/file/list?session_id={session_id}&type=file&order_by=time'
		response=self.send_request('get',url,headers)

	def group_update_file_message(self,headers,file_id):
		# 更新文件并发送信息给群成员
		url=f'/baseapi/wps/file/edit/msg/?fileid={file_id}'
		response=self.send_request('get',url,headers)

	def base_price(self,headers):
		# 获取底价ID以及对应的圈友ID
		url=f'/circle/reserve/list/?search_key=&page=1&pagesize=10'
		response=self.send_request('get',url,headers)
		circle_id=list(filter(lambda x:x['name']=='0底价',response.json()['data']))[0]
		members=list(x['id'] for x in circle_id['member_list'])
		payrate_id=circle_id['pay_rate']['id']
		return members,circle_id['id'],payrate_id

	def add_member_to_price(self,headers,members,circle_id,payrate_id,member):
		# 添加成员到0底价圈友中
		url=f'/orderinfo/circle/link/create/{circle_id}/'
		members=members+member
		body={'name':'0底价','payrate':payrate_id,'to_all_people':0,'circle_type':'markup','member_ids':[members]}
		response=self.send_request('post',url,headers,params=body)

	def creat_sheet(self,headers):
		# 获取询价单ID
		url=f'/iq/inquiry/sheet/create/'
		response=self.send_request('post',url,headers,params={})
		return response.json()['data']['id']

	def set_sheet_information(self,headers,sheet_id,payrate_id=None,files=None):
		# 设置询价单截止时间、标题、添加商品付款比例、附件
		url=f'/iq/inquiry/sheet/edit/{sheet_id}'
		end_time=int(time.time())+700000
		if payrate_id:
			body = {'type': 'payment', 'payment_id': payrate_id}
			response = self.send_request('post', url, headers, params=body)

			body_1 = {'type': 'attachment'}
			response_1 = self.send_request('post', url, headers, params=body_1,files=files)
		else:
			body={'type':'end_time','end_time':end_time}
			response=self.send_request('post',url,headers,params=body)

			body_1={'type':'title','title':'询价'+str(sheet_id)}
			response_1=self.send_request('post',url,headers,params=body_1)

	def add_sales(self,headers,sheet_id,inquiry_name):
		# 添加询价商品
		url=f'/iq/inquiry/sale/add/{sheet_id}'
		body={'inquiry_name':inquiry_name,'inquiry_unit':'个'}
		response=self.send_request('post',url,headers,params=body)
		sale_id=response.json()['data']['id']
		return sale_id

	def add_sale_num(self,headers,sale_id,inquiry_name):
		# 添加询价商品数量
		url=f'/iq/inquiry/sale/edit/{sale_id}'
		body={'action':'modify','inquiry_name':inquiry_name,'inquiry_unit':'个','inquiry_num':100}
		response=self.send_request('post',url,headers,params=body)

	def get_sheet_payrate(self,headers,list_id=[100,0,0,0,0,0]):
		# 获取询价报价专用付款比例
		url=f'/orderinfo/circle/circle_payrate/?rate_type=iq_rate&page=1&key='
		response=self.send_request('get',url,headers)
		if response.json()['data']['payrates']:
			payrate_id=response.json()['data']['payrates'][0]['id']
		else:
			payrate_id=self.add_payrate(headers,list_id)
		return payrate_id

	def add_img_to_sheet(self,headers,sheet_id,files):
		# 添加商品图片
		url=f'/iq/inquiry/sheet/edit/sample/{sheet_id}'
		body={'action':'add'}
		response = self.send_request('post', url, headers, params=body,files=files)

	def release_sheet(self,headers,sheet_id):
		# 提交询价单
		url=f'/iq/inquiry/sheet/release/{sheet_id}'
		body=[]
		response = self.send_request('post', url, headers, params=body)

	def filte_sheet(self,headers,sheet_id):
		# 匹配询价商品
		url=f'/iq/inquiry/sheet/quotes/{sheet_id}'
		body={'action':'filter'}
		response=self.send_request('post',url,headers,params=body)
		if response.json()['data']:
			return True
		else:
			return False

	def continum_sheet(self,headers,sheet_id,payrate_id):
		# 继续向上游询价
		url=f'/iq/inquiry/sheet/transmit/{sheet_id}'
		body={'pay_percent':payrate_id}
		response=self.send_request('post',url,headers,params=body)

	def notice_list(self,headers):
		# 获取公告列表
		url=f'/que/v1/notice/list/create/info/?notice_type=1&page=1&page_size=10&search_key=&type=2&create_user=&time_dict=&push_way=&status='
		response=self.send_request('get',url,headers)

	def notice_info(self,headers,notice_id):
		# 获取公告详情
		url=f'/que/v1/notice/update/info/{notice_id}/'
		response=self.send_request('get',url,headers)

	def test_mock_get(self):
		url='https://c7ed419f-1d20-45cf-99d2-d28258579ca7.mock.pstmn.io/mock/test'
		headers={'x-api-key': 'PMAK-5f98c309f03bdc003bbf8dce-2d564d82f6d56cbd3ed6d1653871cb7615'}
		response=requests.get(url,headers=headers)
		print(response.json())

	def get_nums(self,num):
		a = [x for x in range(num)]
		for i in a:
			yield i

	def get_phonenum(self,nums):
		list_phone=[]
		if nums>=10:
			startnum = time.strftime('%H%M', time.localtime(time.time()))
			for i in range(nums):
				nm=str(i).zfill(4)
				phone_num=f'134{startnum}{nm}'
				list_phone.append(phone_num)
		else:
			startnum=time.strftime('%m%d%H%M', time.localtime(time.time()))
			for i in range(nums):
				phones=int(startnum)+i
				phone_num='134'+str(phones)
				list_phone.append(phone_num)
		print(list_phone)
		return list_phone

if __name__ == '__main__':
	host = 'http://dev.echronos.com:10460'
	aa=All_api(host)
	while True:
		aa.get_phonenum()



