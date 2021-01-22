# -*- coding:utf-8 -*-
from automation_test.api_test.login_information import Login_envirment
from automation_test.api_test.api_information import All_api
from automation_test.api_test.bidding import Bidding
from automation_test import conn_mysql
from concurrent.futures import ThreadPoolExecutor
import threading
import time
from multiprocessing import Pool
import multiprocessing

class Start_use(All_api):

	def get_headers(self,user):
		# 直接登录用户
		host=self.environment
		login_header=Login_envirment(host)
		headers=login_header.get_login_token(user)
		return headers

	def gets_mysql_names(self):
		headers=self.get_headers('duanye')
		mysql_name=self.get_now_use_mysql(headers)
		return mysql_name

	def get_message_from_mysql(self,host,db,sql):
		mysqls=conn_mysql.Operation_mysql()
		try:
			messages = mysqls.get_information(sql, host, db)
			print(messages)
			return messages
		except:
			pass

	def login_swith_company(self,user,type):
		# 登录并切换公司
		login_information = self.get_headers(user)
		company_information = self.get_companys_id(login_information, type)
		self.swith_to_company(login_information, company_information)
		return login_information

	def get_address_id(self,login_information):
		# 获取或者创建新的收货地址
		self.add_application(login_information,47)
		try:
			address_id = self.get_address(login_information)
		except:
			address_id = self.add_address(login_information)
		return address_id

	def get_payrate_id(self,login_information,payrate):
		# 获取或者创建新的付款比例
		self.add_application(login_information,47)
		try:
			payrate_id=self.get_payrate(login_information,payrate)
		except:
			payrate_id = self.add_payrate(login_information,payrate)
		return payrate_id

	def get_transports_id(self,login_information):
		# 获取或者创建新的运费模板
		self.add_application(login_information, 47)
		try:
			transports_id = self.get_transports(login_information)
		except:
			transports_id = self.create_transport(login_information)
		return transports_id

	def balance_or_pay(self, login_information, pay_id, amount):
		# 余额支付或者线下支付
		result = self.balance_pay(login_information, pay_id, amount)
		if result:
			dict_keys = ['payImg']
			files = self.get_img(dict_keys)
			self.fukuan_pay(login_information, pay_id, files)
			return False
		return True

	def batch_googs_pay(self,headers,order_id,condition):
		# 批次付款
		batch_information = self.orderdetail_information(headers, order_id, condition)
		pay_way_batch_1=self.balance_or_pay(headers, batch_information.get('batch_1', '').get('curr_pay_id', ''),batch_information.get('batch_1', '').get('amount', ''))
		pay_way_batch_2 =self.balance_or_pay(headers, batch_information.get('batch_2', '').get('curr_pay_id', ''),batch_information.get('batch_2', '').get('amount', ''))
		batch_information['pay_way_batch_1']=pay_way_batch_1
		batch_information['pay_way_batch_2']=pay_way_batch_2
		return batch_information

	def batch_shoukuan(self,headers,batch_information):
		# 批次收款
		self.shoukuan_pay(headers, batch_information.get('batch_2', '').get('curr_pay_id', ''),batch_information.get('batch_2', '').get('amount', ''),batch_information.get('pay_way_batch_2',''))
		self.shoukuan_pay(headers, batch_information.get('batch_1', '').get('curr_pay_id', ''),batch_information.get('batch_1', '').get('amount', ''),batch_information.get('pay_way_batch_1',''))

	def send_goods_from_scs(self,headers,order_id,snap_ids,files):
		# 批次发货
		self.get_batch_goods_1(headers, snap_ids)
		self.right_batch_goods(headers, snap_ids)
		self.get_batch_goods_2(headers, snap_ids)
		self.send_batch_goods(headers, order_id, snap_ids,files)

class Make_moudle(Start_use):

	"""登录账户，获取对应的cookies"""
	def set_cookies(self,users):
		self.shigongfang_cookies = self.login_swith_company(users['shigongfang']['fuzheren'],users['shigongfang']['account_type'])
		self.hualifang_cookies = self.login_swith_company(users['hualifang']['fuzheren'],users['hualifang']['account_type'])
		self.qudaoshang_cookies = self.login_swith_company(users['qudaoshang']['fuzheren'],users['qudaoshang']['account_type'])
		self.huayuansu_cookies = self.login_swith_company(users['huayuansu']['fuzheren'],users['huayuansu']['account_type'])
		self.changshang_cookies = self.login_swith_company(users['changshang']['fuzheren'],users['changshang']['account_type'])

	"""公司认证"""
	def prove_company(self,names):
		print('--------公司认证流程，执行开始---------')
		login_informations = {}
		list_names = ['工程方', '渠道商', '生产商']
		for num,list_name in enumerate(list_names):
			phone_num= self.sign_in(num)
			login_information =self.get_headers(phone_num['login_name'])
			if list_name == '生产商':
				company_id=self.add_personal_company(login_information)
				dict_keys=['brandLogo']
				files=self.get_img(dict_keys)
				self.add_brands(login_information,company_id,files)
			company_name = self.company_name(login_information, names, num)
			company_prove_information = self.company_information(login_information, company_name)
			dict_keys = ['legal_person_IdCard', 'co_license', 'logo']
			files = self.get_img(dict_keys)
			self.company_prove(login_information, company_prove_information, files, list_name)
			if list_name == '生产商':
				login_information = self.huayuansu_cookies
			else:
				login_information = self.hualifang_cookies
			crm_company_id = self.company_prove_id(login_information, company_prove_information)
			self.compare_company_prove(login_information,crm_company_id)
			login_informations[list_names[num]] = {'company_name': company_prove_information['name'],
												   'login_name': phone_num['login_name']}
		print(login_informations)
		print('--------公司认证流程，执行完成---------')
		return login_informations

	"""授予权限"""
	def add_personal_give_roles(self, users):
		print('--------注册并添加到组织架构，授予全部权限流程，执行开始---------')
		phone = []
		for i, username in enumerate(users):
			login_infor = self.sign_in(i)
			phone_num = login_infor['login_name']
			phone.append(phone_num)
			user = users[username]
			company_id = user['company_id']
			if username in ('hualifang', 'huayuansu'):
				login_information = self.get_headers(user['shenpi'])
				department_id = self.get_department_id(login_information)
				self.add_personal_to_company(login_information, phone_num, department_id)
				role_id = self.role_list(login_information, phone_num)
				self.get_son_company(login_information, role_id, company_id)
				login_information = self.login_swith_company(user['fuzheren'], user['account_type'])
			else:
				login_information = self.login_swith_company(user['fuzheren'], user['account_type'])
				self.add_personal_to_company(login_information, phone_num, company_id)
			template_list = self.get_template_list(login_information)
			user_id = self.member_rolelist(login_information, phone_num)
			add_role_id = None
			if username in ('hualifang', 'huayuansu'):
				add_role_id = self.get_roles_id(login_information)
				if not add_role_id:
					add_role_id = self.get_role_id(login_information)
					self.add_role_lists(login_information, add_role_id, username)
			self.give_roles_to_users(login_information, user_id, template_list['name'], username, role_id=add_role_id)
		print(phone)
		return phone

	"""上架商品并设置圈层价-战采"""
	def upload_goods_to_circle(self,scales, companys,payrate_ids,catelog_id,price,is_stop=None):
		headers = self.changshang_cookies
		transport_id=self.get_transports_id(headers)
		self.add_application(headers, 26)
		sale_id = self.batch_goods(headers, transport_id, catelog_id, price) # 批量上架
		if is_stop=='批量上架商品完成':
			return
		payrate_id=self.get_payrate_id(headers,payrate_ids['changshang_to_huayuansu'])
		self.set_circle_price(headers, sale_id['sale_id'],scales['changshang_to_huayuansu'],companys['huayuansu']['company_id'],payrate_id)
		if is_stop=='待华元素审批圈层价':
			return
		headers = self.huayuansu_cookies
		self.approval_circle_price(headers)
		payrate_id = self.get_payrate_id(headers, payrate_ids['huayuansu_to_hualifang'])
		circle_price_id_to_hualifang = self.set_circle_price(headers, sale_id['sale_id'],scales['huayuansu_to_hualifang'], companys['hualifang']['company_id'],payrate_id)
		headers = self.hualifang_cookies
		payrate_id = self.get_payrate_id(headers, payrate_ids['hualifang_to_shigongfang'])
		circle_price_id_to_shigongfang = self.set_circle_price(headers, sale_id['sale_id'], scales['hualifang_to_shigongfang'], companys['shigongfang']['company_id'],payrate_id)
		sale_dict = {'product_id_1': sale_id['sale_id'][0], 'product_id_2': sale_id['sale_id'][1]}
		print(sale_dict)
		return sale_dict

	"""上架商品并设置圈层价-渠道"""
	def upload_goods_channel(self,scales, companys,payrate_ids, choice=None):
		headers = self.changshang_cookies
		transport_id = self.get_transports_id(headers)
		if choice:
			sale_id = self.goods_shelves(headers)  # 简单上架
		else:
			sale_id = self.batch_goods(headers, transport_id)  # 批量上架
		payrate_id=self.get_payrate_id(headers,payrate_ids['changshang_to_huayuansu'])
		self.set_circle_price(headers, sale_id['sale_id'],scales['changshang_to_huayuansu'],companys['huayuansu']['company_id'],payrate_id)
		headers = self.huayuansu_cookies
		self.approval_circle_price(headers)
		payrate_id = self.get_payrate_id(headers, payrate_ids['huayuansu_to_qudaoshang'])
		circle_price_id_to_qudaoshang = self.set_circle_price(headers, sale_id['sale_id'],scales['huayuansu_to_qudaoshang'], companys['qudaoshang']['company_id'],payrate_id)
		sale_dict = {'product_id_1': sale_id['sale_id'][0], 'product_id_2': sale_id['sale_id'][1]}
		print(sale_dict)

	"""施工方订单流程"""
	def start_from_shihongfang(self,login_information,sale_id):
		self.add_batch_to_cart(login_information, sale_id)
		list_id = self.sale_list(login_information, sale_id)
		self.updateSaleCartNum(login_information,list_id)
		self.sale_list(login_information, sale_id)
		address_id = self.get_address_id(login_information)
		self.creat_order(login_information,list_id)
		order_id = self.cartorderpost(login_information, list_id, address_id)
		order_condition = '关联订单'
		older_order = self.orderdetail_information(login_information,order_id['order_id'],  order_condition)
		if older_order.get('预付款', ''):
			pay_way=self.balance_or_pay(login_information, older_order.get('预付款', '').get('curr_pay_id', ''), older_order.get('预付款', '').get('amount', ''))
			older_order['pay_way']=pay_way
		return older_order

	"""华立方订单流程"""
	def start_from_hualifang(self,order_information,payrate_ids,condition=None,is_stop=None):
		print('----------华立方收付款：战采----------')
		login_information = self.hualifang_cookies
		if order_information.get('预付款', ''):
			self.shoukuan_pay(login_information,order_information.get('预付款', '').get('curr_pay_id', ''), order_information.get('预付款', '').get('amount', ''),order_information.get('pay_way', ''))
		if is_stop=='华立方分单':
			return
		order_condition = '分单商品信息'
		snap_details = self.orderdetail_information(login_information,order_information.get('curr_id',''),order_condition)
		pay_rate_id_1 = self.get_payrate_id(login_information,payrate_ids[0])
		pay_rate_id_2 = self.get_payrate_id(login_information,payrate_ids[1])
		pay_rate_id_3 = self.get_payrate_id(login_information,payrate_ids[2])
		pay_rate_id=[pay_rate_id_1,pay_rate_id_2,pay_rate_id_3]
		self.split_order(login_information,order_information.get('curr_id',''), snap_details, pay_rate_id,condition)
		dfr_order_id = self.new_order(login_information, order_information.get('curr_id',''))
		if condition:
			if is_stop=='渠道商接单':
				return
			login_information = self.qudaoshang_cookies
			self.active_order(login_information, dfr_order_id)
			login_information = self.hualifang_cookies
		order_condition = '关联订单'
		curr_order = self.orderdetail_information(login_information,dfr_order_id, order_condition)
		if curr_order.get('预付款', ''):
			pay_way=self.balance_or_pay(login_information, curr_order.get('预付款', '').get('curr_pay_id', ''), curr_order.get('预付款', '').get('amount', ''))
			curr_order['pay_way']=pay_way
		return curr_order

	"""渠道商订单流程"""
	def start_from_qudaoshang(self, order_information,condition=None):
		print('----------渠道商收付款：战采----------')
		login_information = self.qudaoshang_cookies
		if order_information.get('预付款', ''):
			self.shoukuan_pay(login_information,order_information.get('预付款', '').get('curr_pay_id', ''), order_information.get('预付款', '').get('amount', ''),order_information.get('pay_way', ''))
		if condition==1:
			return False
		else:
			dfr_order_id = self.new_order(login_information,order_information.get('curr_id',''))
			order_condition = '关联订单'
			new_order_information = self.orderdetail_information(login_information,dfr_order_id,  order_condition)
			if new_order_information.get('预付款', ''):
				pay_way=self.balance_or_pay(login_information, new_order_information.get('预付款', '').get('curr_pay_id', ''), new_order_information.get('预付款', '').get('amount', ''))
				new_order_information['pay_way']=pay_way
			return new_order_information

	"""华元素订单流程"""
	def start_from_huayuansu(self,login_information,curr_order):
		if curr_order.get('预付款', ''):
			self.shoukuan_pay(login_information,curr_order.get('预付款', '').get('curr_pay_id', ''), curr_order.get('预付款', '').get('amount', ''),curr_order.get('pay_way',''))
		new_order_id = self.new_order(login_information,curr_order['curr_id'])
		order_condition = '关联订单'
		new_order = self.orderdetail_information(login_information,new_order_id,  order_condition)
		if new_order.get('预付款', ''):
			pay_way=self.balance_or_pay(login_information, new_order.get('预付款', '').get('curr_pay_id', ''), new_order.get('预付款', '').get('amount', ''))
			new_order['pay_way']=pay_way
		return new_order

	"""生产商订单流程"""
	def start_from_shengchanshang(self,new_order):
		print('----------生产商收款、备货----------')
		login_information = self.changshang_cookies
		if new_order.get('预付款', ''):
			self.shoukuan_pay(login_information,new_order.get('预付款', '').get('curr_pay_id', ''), new_order.get('预付款', '').get('amount', ''),new_order.get('pay_way',''))
		self.prepare_goods(login_information, new_order['curr_id'])

	"""下游充值"""
	def down_recharge_cash(self,headers,companys):
		cash_id = self.cash_list_id(headers, companys)
		cash_information = self.pay_cash_information(headers, cash_id)
		dict_keys = ['pay_img']
		files = self.get_img(dict_keys)
		self.pay_cash_to_up(headers, cash_information,cash_id,files)
		return cash_information

	"""上游收款"""
	def up_recharge_cash(self,headers,cash_information,companys=None):
		pay_id=self.get_up_cash(headers,cash_information)
		self.pay_up_cash(headers,pay_id)
		if companys:
			new_cash_information=self.down_recharge_cash(headers,companys)
			return new_cash_information

	"""下游询价"""
	def add_down_inquiry(self,headers,inquiry_name='没有哒'):
		sheet_id=self.creat_sheet(headers)
		self.set_sheet_information(headers,sheet_id)
		sale_id=self.add_sales(headers,sheet_id,inquiry_name)
		self.add_sale_num(headers,sale_id,inquiry_name)
		dict_key='attachment'
		files=self.get_img(dict_key)
		payrate_id=self.get_sheet_payrate(headers)
		self.set_sheet_information(headers,sheet_id,payrate_id=payrate_id,files=files)
		files = [('sample', open(f'123.jpg','rb'))]
		self.add_img_to_sheet(headers,sheet_id,files)
		self.release_sheet(headers,sheet_id)
		sheet_information={'sheet_id':sheet_id,'payrate_id':payrate_id}
		return sheet_information

	"""上游报价"""
	def add_up_inquiry(self,headers,sheet_information,mode=None):
		sheet_id=sheet_information.get('sheet_id')
		payrate_id=sheet_information.get('payrate_id')
		condition=self.filte_sheet(headers,sheet_id)
		if condition:
			print(1111)
		else:
			if mode:
				print(2222)
			else:
				self.continum_sheet(headers,sheet_id,payrate_id)

class Use_modle(Make_moudle,Bidding):

	"""仅订单流程-战采"""
	def only_order_process(self, sale_ids,payrate_ids,condition=None,lock=None):
		# 仅订单流程-战采
		print('施工方开始下订单'.center(20,'='))
		login_information = self.shigongfang_cookies

		if lock:
			lock.acquire()
			sgf_to_hlf_order=self.start_from_shihongfang(login_information,sale_ids)
			lock.release()
		else:
			sgf_to_hlf_order = self.start_from_shihongfang(login_information, sale_ids)

		payrate_id =[payrate_ids.get('hualifang_to_qudaoshang'),payrate_ids.get('huayuansu_to_qudaoshang'),payrate_ids.get('huayuansu_to_hualifang')]
		hlf_to_qds_order=self.start_from_hualifang(sgf_to_hlf_order,payrate_id,condition)
		if condition:
			qds_to_hys_order=self.start_from_qudaoshang(hlf_to_qds_order)
		else:
			qds_to_hys_order=hlf_to_qds_order
		print('----------华元素收付款----------')
		login_information = self.huayuansu_cookies
		hys_to_scs_order=self.start_from_huayuansu(login_information,qds_to_hys_order)
		self.start_from_shengchanshang(hys_to_scs_order)

	"""战采全流程"""
	def all_order_process(self,sale_ids,payrate_ids,condition=None,is_stop=None):
		# 赋值两两交易之间的付款比例
		sgf_to_hlf_payrate_id = payrate_ids.get('hualifang_to_shigongfang')
		hlf_to_qds_payrate_id = payrate_ids.get('hualifang_to_qudaoshang')
		qds_to_hys_payrate_id = payrate_ids.get('huayuansu_to_qudaoshang')
		hys_to_scs_payrate_id = payrate_ids.get('changshang_to_huayuansu')
		payrate_id = [hlf_to_qds_payrate_id, qds_to_hys_payrate_id,qds_to_hys_payrate_id]

		# 赋值登录cookies
		sgf_cookies=self.shigongfang_cookies
		hlf_cookies=self.hualifang_cookies
		qds_cookies=self.qudaoshang_cookies
		hys_cookies=self.huayuansu_cookies
		scs_cookies=self.changshang_cookies

		self.ptinfo('订单全流程')
		self.ptinfo('施工方开始下订单')
		sgf_to_hlf_order = self.start_from_shihongfang(sgf_cookies, sale_ids)
		if is_stop=='施工方提交订单':
			return
		hlf_to_qds_order=self.start_from_hualifang(sgf_to_hlf_order,payrate_id,condition=1,is_stop=is_stop)
		qds_to_hys_order=self.start_from_qudaoshang(hlf_to_qds_order)
		print('----------华元素收付款----------')
		hys_to_scs_order=self.start_from_huayuansu(hys_cookies,qds_to_hys_order)
		self.start_from_shengchanshang(hys_to_scs_order)
		if is_stop=='生产商备货完成':
			return

		if condition:
			"""分批"""
			print('----------施工方货物分批----------')
			snap_ids=self.split_snap_id(sgf_cookies,sgf_to_hlf_order.get('curr_id',''),'分批')
			self.split_goods(sgf_cookies,sgf_to_hlf_order.get('curr_id',''),snap_ids)

			if sgf_to_hlf_payrate_id[1]:
				print('----------收付发货款----------')
				"""施工方批次付款"""
				sgf_to_hlf_batch=self.batch_googs_pay(sgf_cookies,sgf_to_hlf_order.get('curr_id',''),'发货分批')

				"""华立方批次收款-付款"""
				self.batch_shoukuan(hlf_cookies,sgf_to_hlf_batch)
			if hlf_to_qds_payrate_id[1]:
				hlf_to_qds_batch = self.batch_googs_pay(hlf_cookies,hlf_to_qds_order.get('curr_id',''),'发货分批')

				"""渠道商批次收款-付款"""
				self.batch_shoukuan(qds_cookies, hlf_to_qds_batch)
			if qds_to_hys_payrate_id[1]:
				qds_to_hys_batch = self.batch_googs_pay(qds_cookies, qds_to_hys_order.get('curr_id', ''),'发货分批')

				"""华元素批次收款-付款"""
				self.batch_shoukuan(hys_cookies, qds_to_hys_batch)
			if hys_to_scs_payrate_id[1]:
				hys_to_scs_batch = self.batch_googs_pay(hys_cookies, hys_to_scs_order.get('curr_id', ''),'发货分批')

				"""生产商批次收款-付款"""
				self.batch_shoukuan(scs_cookies, hys_to_scs_batch)

			print('----------生产商发货----------')
			snap_ids=self.split_snap_id(scs_cookies,hys_to_scs_order['curr_id'],'发货')
			dict_keys = ['hegezheng']
			files = self.get_img(dict_keys)
			self.send_goods_from_scs(scs_cookies,hys_to_scs_order.get('curr_id', ''),snap_ids.get('batches_list_1', ''),files)

			self.send_goods_from_scs(scs_cookies, hys_to_scs_order.get('curr_id', ''), snap_ids.get('batches_list_2', ''),files)

			if is_stop=='施工方到货验收':
				return
			print('----------到货验收----------')
			snap_ids=self.split_snap_id(sgf_cookies,sgf_to_hlf_order.get('curr_id', ''),'发货')
			dict_keys = ['yanshou']
			files = self.get_img(dict_keys)

			self.give_batch_goods_1(sgf_cookies,sgf_to_hlf_order.get('curr_id', ''), snap_ids.get('batches_list_1', ''))
			self.check_batch_goods(sgf_cookies, sgf_to_hlf_order.get('curr_id', ''), snap_ids.get('batches_list_1', ''))
			self.give_batch_goods_1(sgf_cookies, sgf_to_hlf_order.get('curr_id', ''), snap_ids.get('batches_list_1', ''))
			self.check_batch_start(sgf_cookies,sgf_to_hlf_order.get('curr_id', ''),snap_ids.get('batches_list_1', ''),files)

			self.give_batch_goods_1(sgf_cookies, sgf_to_hlf_order.get('curr_id', ''), snap_ids.get('batches_list_2', ''))
			self.check_batch_goods(sgf_cookies, sgf_to_hlf_order.get('curr_id', ''), snap_ids.get('batches_list_2', ''))
			self.give_batch_goods_1(sgf_cookies, sgf_to_hlf_order.get('curr_id', ''), snap_ids.get('batches_list_2', ''))
			self.check_batch_start(sgf_cookies, sgf_to_hlf_order.get('curr_id', ''), snap_ids.get('batches_list_2', ''),files)

			if is_stop=='华立方到货验收':
				return
			snap_ids = self.split_snap_id(hlf_cookies, hlf_to_qds_order.get('curr_id', ''), '发货')
			self.check_batch_middle(hlf_cookies,hlf_to_qds_order.get('curr_id', ''),snap_ids.get('batches_list_1', ''))
			self.check_batch_middle(hlf_cookies,hlf_to_qds_order.get('curr_id', ''),snap_ids.get('batches_list_2', ''))

			if is_stop=='华元素到货验收':
				return
			snap_ids = self.split_snap_id(hys_cookies, hys_to_scs_order.get('curr_id', ''), '发货')
			self.check_batch_middle(hys_cookies, hys_to_scs_order.get('curr_id', ''),snap_ids.get('batches_list_1', ''))
			self.check_batch_middle(hys_cookies, hys_to_scs_order.get('curr_id', ''),snap_ids.get('batches_list_2', ''))

			if is_stop=='华元素到货验收完成':
				return
			if sgf_to_hlf_payrate_id[2]:
				print('----------收付分批发货款----------')
				"""施工方批次付款"""
				sgf_to_hlf_batch=self.batch_googs_pay(sgf_cookies,sgf_to_hlf_order.get('curr_id',''),'到货分批')

				"""华立方批次收款-付款"""
				self.batch_shoukuan(hlf_cookies,sgf_to_hlf_batch)
			if hlf_to_qds_payrate_id[2]:
				hlf_to_qds_batch = self.batch_googs_pay(hlf_cookies,hlf_to_qds_order.get('curr_id',''),'到货分批')

				"""渠道商批次收款-付款"""
				self.batch_shoukuan(qds_cookies, hlf_to_qds_batch)
			if qds_to_hys_payrate_id[2]:
				qds_to_hys_batch = self.batch_googs_pay(qds_cookies, qds_to_hys_order.get('curr_id', ''),'到货分批')

				"""华元素批次收款-付款"""
				self.batch_shoukuan(hys_cookies, qds_to_hys_batch)
			if hys_to_scs_payrate_id[2]:
				hys_to_scs_batch = self.batch_googs_pay(hys_cookies, hys_to_scs_order.get('curr_id', ''),'到货分批')

				"""生产商批次收款-付款"""
				self.batch_shoukuan(scs_cookies, hys_to_scs_batch)

		else:
			"""不分批"""
			if sgf_to_hlf_payrate_id[1]:
				print('----------收付发货款----------')
				pay_way=self.balance_or_pay(sgf_cookies, sgf_to_hlf_order.get('发货款', '').get('curr_pay_id', ''), sgf_to_hlf_order.get('发货款', '').get('amount', ''))

				self.shoukuan_pay(hlf_cookies, sgf_to_hlf_order.get('发货款', '').get('curr_pay_id', ''), sgf_to_hlf_order.get('发货款', '').get('amount', ''),pay_way)
			if hlf_to_qds_payrate_id[1]:
				pay_way=self.balance_or_pay(hlf_cookies, hlf_to_qds_order.get('发货款', '').get('curr_pay_id', ''), hlf_to_qds_order.get('发货款', '').get('amount', ''))

				self.shoukuan_pay(qds_cookies, hlf_to_qds_order.get('发货款', '').get('curr_pay_id', ''), hlf_to_qds_order.get('发货款', '').get('amount', ''),pay_way)
			if qds_to_hys_payrate_id[1]:
				pay_way=self.balance_or_pay(qds_cookies, qds_to_hys_order.get('发货款', '').get('curr_pay_id', ''), qds_to_hys_order.get('发货款', '').get('amount', ''))

				self.shoukuan_pay(hys_cookies, qds_to_hys_order.get('发货款', '').get('curr_pay_id', ''), qds_to_hys_order.get('发货款', '').get('amount', ''),pay_way)
			if hys_to_scs_payrate_id[1]:
				pay_way=self.balance_or_pay(hys_cookies, hys_to_scs_order.get('发货款', '').get('curr_pay_id', ''), hys_to_scs_order.get('发货款', '').get('amount', ''))

				self.shoukuan_pay(scs_cookies, hys_to_scs_order.get('发货款', '').get('curr_pay_id', ''), hys_to_scs_order.get('发货款', '').get('amount', ''),pay_way)

			print('----------生产商一次发货----------')
			snap_id_fahuo = self.get_goods_information(scs_cookies,hys_to_scs_order['curr_id'])
			dict_keys = ['hegezheng']
			files = self.get_img(dict_keys)
			self.right_goods(scs_cookies, snap_id_fahuo, hys_to_scs_order['curr_id'])
			self.delivery_goods(scs_cookies, hys_to_scs_order['curr_id'], files)

			if is_stop=='生产商发货完成':
				return
			print('----------到货验收----------')
			snap_id_yanshou = self.ckeck_goods_information(sgf_cookies,sgf_to_hlf_order['curr_id'])
			self.right_check_goods(sgf_cookies, snap_id_yanshou, sgf_to_hlf_order['curr_id'])
			dict_keys = ['yanshou']
			files = self.get_img(dict_keys)
			if is_stop == '施工方到货验收':
				return
			self.check_goods(sgf_cookies, sgf_to_hlf_order['curr_id'], files)
			if is_stop == '华立方到货验收':
				return
			self.orderinfo_check_goods(hlf_cookies, hlf_to_qds_order['curr_id'])
			if is_stop == '华元素到货验收':
				return
			self.orderinfo_check_goods(hys_cookies, hys_to_scs_order['curr_id'])

			if sgf_to_hlf_payrate_id[2]:
				print('----------付到货款----------')
				pay_way=self.balance_or_pay(sgf_cookies, sgf_to_hlf_order.get('到货款', '').get('curr_pay_id', ''), sgf_to_hlf_order.get('到货款', '').get('amount', ''))

				self.shoukuan_pay(hlf_cookies, sgf_to_hlf_order.get('到货款', '').get('curr_pay_id', ''), sgf_to_hlf_order.get('到货款', '').get('amount', ''),pay_way)
			if hlf_to_qds_payrate_id[2]:
				pay_way=self.balance_or_pay(hlf_cookies, hlf_to_qds_order.get('到货款', '').get('curr_pay_id', ''), hlf_to_qds_order.get('到货款', '').get('amount', ''))

				self.shoukuan_pay(qds_cookies, hlf_to_qds_order.get('到货款', '').get('curr_pay_id', ''), hlf_to_qds_order.get('到货款', '').get('amount', ''),pay_way)
			if qds_to_hys_payrate_id[2]:
				pay_way=self.balance_or_pay(qds_cookies, qds_to_hys_order.get('到货款', '').get('curr_pay_id', ''), qds_to_hys_order.get('到货款', '').get('amount', ''))

				self.shoukuan_pay(hys_cookies, qds_to_hys_order.get('到货款', '').get('curr_pay_id', ''), qds_to_hys_order.get('到货款', '').get('amount', ''),pay_way)
			if hys_to_scs_payrate_id[2]:
				pay_way=self.balance_or_pay(hys_cookies, hys_to_scs_order.get('到货款', '').get('curr_pay_id', ''), hys_to_scs_order.get('到货款', '').get('amount', ''))

				self.shoukuan_pay(scs_cookies, hys_to_scs_order.get('到货款', '').get('curr_pay_id', ''), hys_to_scs_order.get('到货款', '').get('amount', ''),pay_way)

		print('----------安装----------')
		dict_keys = ['hegezheng']
		files = self.get_img(dict_keys)
		self.install_goods(scs_cookies, hys_to_scs_order['curr_id'], files)
		self.install_goods(hys_cookies, qds_to_hys_order['curr_id'], files)
		self.install_goods(hlf_cookies, sgf_to_hlf_order['curr_id'], files)

		print('----------安装验收----------')
		dict_keys = ['hegezheng','ff1']
		files = self.get_img(dict_keys)
		self.check_install(sgf_cookies, sgf_to_hlf_order['curr_id'],files)
		self.check_install(hlf_cookies, hlf_to_qds_order['curr_id'])
		self.check_install(hys_cookies, hys_to_scs_order['curr_id'])

		if sgf_to_hlf_payrate_id[3]:
			print('----------收付安装款----------')
			pay_way=self.balance_or_pay(sgf_cookies, sgf_to_hlf_order.get('安装款', '').get('curr_pay_id', ''), sgf_to_hlf_order.get('安装款', '').get('amount', ''))

			self.shoukuan_pay(hlf_cookies, sgf_to_hlf_order.get('安装款', '').get('curr_pay_id', ''), sgf_to_hlf_order.get('安装款', '').get('amount', ''),pay_way)
		if hlf_to_qds_payrate_id[3]:
			pay_way=self.balance_or_pay(hlf_cookies, hlf_to_qds_order.get('安装款', '').get('curr_pay_id', ''), hlf_to_qds_order.get('安装款', '').get('amount', ''))

			self.shoukuan_pay(qds_cookies, hlf_to_qds_order.get('安装款', '').get('curr_pay_id', ''), hlf_to_qds_order.get('安装款', '').get('amount', ''),pay_way)
		if qds_to_hys_payrate_id[3]:
			pay_way=self.balance_or_pay(qds_cookies, qds_to_hys_order.get('安装款', '').get('curr_pay_id', ''), qds_to_hys_order.get('安装款', '').get('amount', ''))

			self.shoukuan_pay(hys_cookies, qds_to_hys_order.get('安装款', '').get('curr_pay_id', ''), qds_to_hys_order.get('安装款', '').get('amount', ''),pay_way)
		if hys_to_scs_payrate_id[3]:
			pay_way=self.balance_or_pay(hys_cookies, hys_to_scs_order.get('安装款', '').get('curr_pay_id', ''), hys_to_scs_order.get('安装款', '').get('amount', ''))

			self.shoukuan_pay(scs_cookies, hys_to_scs_order.get('安装款', '').get('curr_pay_id', ''), hys_to_scs_order.get('安装款', '').get('amount', ''),pay_way)

		print('----------结算验收----------')
		self.account_check(scs_cookies, hys_to_scs_order['curr_id'])
		self.account_check(hys_cookies, qds_to_hys_order['curr_id'])
		self.account_check(hlf_cookies, sgf_to_hlf_order['curr_id'])

		if sgf_to_hlf_payrate_id[4]:
			print('----------收付结算款----------')
			pay_way=self.balance_or_pay(sgf_cookies, sgf_to_hlf_order.get('结算款', '').get('curr_pay_id', ''), sgf_to_hlf_order.get('结算款', '').get('amount', ''))

			self.shoukuan_pay(hlf_cookies, sgf_to_hlf_order.get('结算款', '').get('curr_pay_id', ''), sgf_to_hlf_order.get('结算款', '').get('amount', ''),pay_way)
		if hlf_to_qds_payrate_id[4]:
			pay_way=self.balance_or_pay(hlf_cookies, hlf_to_qds_order.get('结算款', '').get('curr_pay_id', ''), hlf_to_qds_order.get('结算款', '').get('amount', ''))

			self.shoukuan_pay(qds_cookies, hlf_to_qds_order.get('结算款', '').get('curr_pay_id', ''), hlf_to_qds_order.get('结算款', '').get('amount', ''),pay_way)
		if qds_to_hys_payrate_id[4]:
			pay_way=self.balance_or_pay(qds_cookies, qds_to_hys_order.get('结算款', '').get('curr_pay_id', ''), qds_to_hys_order.get('结算款', '').get('amount', ''))

			self.shoukuan_pay(hys_cookies, qds_to_hys_order.get('结算款', '').get('curr_pay_id', ''), qds_to_hys_order.get('结算款', '').get('amount', ''),pay_way)
		if hys_to_scs_payrate_id[4]:
			pay_way=self.balance_or_pay(hys_cookies, hys_to_scs_order.get('结算款', '').get('curr_pay_id', ''), hys_to_scs_order.get('结算款', '').get('amount', ''))

			self.shoukuan_pay(scs_cookies, hys_to_scs_order.get('结算款', '').get('curr_pay_id', ''), hys_to_scs_order.get('结算款', '').get('amount', ''),pay_way)

		print('----------质保结束----------')
		dict_keys = ['hegezheng']
		files = self.get_img(dict_keys)
		self.complete_insurance(scs_cookies, hys_to_scs_order['curr_id'],files)
		self.complete_insurance(hys_cookies, qds_to_hys_order['curr_id'],files)
		self.complete_insurance(hlf_cookies, sgf_to_hlf_order['curr_id'],files)

		if sgf_to_hlf_payrate_id[5]:
			print('----------收付质保金----------')
			pay_way=self.balance_or_pay(sgf_cookies, sgf_to_hlf_order.get('质保金', '').get('curr_pay_id', ''), sgf_to_hlf_order.get('质保金', '').get('amount', ''))

			self.shoukuan_pay(hlf_cookies, sgf_to_hlf_order.get('质保金', '').get('curr_pay_id', ''), sgf_to_hlf_order.get('质保金', '').get('amount', ''),pay_way)
		if hlf_to_qds_payrate_id[5]:
			pay_way=self.balance_or_pay(hlf_cookies, hlf_to_qds_order.get('质保金', '').get('curr_pay_id', ''), hlf_to_qds_order.get('质保金', '').get('amount', ''))

			self.shoukuan_pay(qds_cookies, hlf_to_qds_order.get('质保金', '').get('curr_pay_id', ''), hlf_to_qds_order.get('质保金', '').get('amount', ''),pay_way)
		if qds_to_hys_payrate_id[5]:
			pay_way=self.balance_or_pay(qds_cookies, qds_to_hys_order.get('质保金', '').get('curr_pay_id', ''), qds_to_hys_order.get('质保金', '').get('amount', ''))

			self.shoukuan_pay(hys_cookies, qds_to_hys_order.get('质保金', '').get('curr_pay_id', ''), qds_to_hys_order.get('质保金', '').get('amount', ''),pay_way)
		if hys_to_scs_payrate_id[5]:
			pay_way=self.balance_or_pay(hys_cookies, hys_to_scs_order.get('质保金', '').get('curr_pay_id', ''), hys_to_scs_order.get('质保金', '').get('amount', ''))

			self.shoukuan_pay(scs_cookies, hys_to_scs_order.get('质保金', '').get('curr_pay_id', ''), hys_to_scs_order.get('质保金', '').get('amount', ''),pay_way)

	"""渠道、特殊战采流程"""
	def channel_order_process(self,sale_ids,payrate_ids,batch=None,condition=None):

		if condition==2:
			print('----------渠道流程----------')
			qds_cookies=self.qudaoshang_cookies
			hys_cookies=self.huayuansu_cookies
			scs_cookies=self.changshang_cookies
			qds_to_hys_order=self.start_from_shihongfang(qds_cookies,sale_ids)
			hys_to_scs_order=self.start_from_huayuansu(hys_cookies,qds_to_hys_order)
			self.start_from_shengchanshang(hys_to_scs_order)
			qds_to_hys_payrate_id = payrate_ids.get('huayuansu_to_qudaoshang')
			hys_to_scs_payrate_id = payrate_ids.get('changshang_to_huayuansu')

		elif condition==1:
			print('----------特殊战采流程----------')
			qds_cookies = self.shigongfang_cookies
			hys_cookies = self.hualifang_cookies
			scs_cookies = self.qudaoshang_cookies
			qds_to_hys_order = self.start_from_shihongfang(qds_cookies, sale_ids)
			payrate_id=[payrate_ids.get('hualifang_to_qudaoshang'),payrate_ids.get('hualifang_to_qudaoshang'),payrate_ids.get('hualifang_to_qudaoshang')]
			hys_to_scs_order = self.start_from_hualifang(qds_to_hys_order,payrate_id,condition=2)
			self.start_from_qudaoshang(hys_to_scs_order,condition=1)
			self.prepare_goods(scs_cookies, hys_to_scs_order['curr_id'])

			qds_to_hys_payrate_id = payrate_ids.get('hualifang_to_shigongfang')
			hys_to_scs_payrate_id = payrate_ids.get('hualifang_to_qudaoshang')

		else:
			return False

		"""是否分批"""
		if batch==1:
			print('----------渠道商货物分批----------')
			snap_ids = self.split_snap_id(qds_cookies, qds_to_hys_order.get('curr_id', ''), '分批')
			self.split_goods(qds_cookies, qds_to_hys_order.get('curr_id', ''), snap_ids)

			"""渠道商批次付款"""
			if qds_to_hys_payrate_id[1]:
				qds_to_hys_batch = self.batch_googs_pay(qds_cookies, qds_to_hys_order.get('curr_id', ''), '发货分批')

				"""华元素批次收款-付款"""
				self.batch_shoukuan(hys_cookies, qds_to_hys_batch)
			if hys_to_scs_payrate_id[1]:
				hys_to_scs_batch = self.batch_googs_pay(hys_cookies, hys_to_scs_order.get('curr_id', ''), '发货分批')

				"""生产商批次收款-付款"""
				self.batch_shoukuan(scs_cookies, hys_to_scs_batch)

			print('----------生产商发货----------')
			snap_ids = self.split_snap_id(scs_cookies, hys_to_scs_order['curr_id'], '发货')
			dict_keys = ['hegezheng']
			files = self.get_img(dict_keys)
			self.send_goods_from_scs(scs_cookies, hys_to_scs_order.get('curr_id', ''),
									 snap_ids.get('batches_list_1', ''), files)

			self.send_goods_from_scs(scs_cookies, hys_to_scs_order.get('curr_id', ''),
									 snap_ids.get('batches_list_2', ''), files)

			print('----------到货验收----------')
			snap_ids = self.split_snap_id(qds_cookies, qds_to_hys_order.get('curr_id', ''), '发货')
			dict_keys = ['yanshou']
			files = self.get_img(dict_keys)

			self.give_batch_goods_1(qds_cookies, qds_to_hys_order.get('curr_id', ''),
									snap_ids.get('batches_list_1', ''))
			self.check_batch_goods(qds_cookies, qds_to_hys_order.get('curr_id', ''),
								   snap_ids.get('batches_list_1', ''))
			self.give_batch_goods_1(qds_cookies, qds_to_hys_order.get('curr_id', ''),
									snap_ids.get('batches_list_1', ''))
			self.check_batch_start(qds_cookies, qds_to_hys_order.get('curr_id', ''),
								   snap_ids.get('batches_list_1', ''), files)

			self.give_batch_goods_1(qds_cookies, qds_to_hys_order.get('curr_id', ''),
									snap_ids.get('batches_list_2', ''))
			self.check_batch_goods(qds_cookies, qds_to_hys_order.get('curr_id', ''),
								   snap_ids.get('batches_list_2', ''))
			self.give_batch_goods_1(qds_cookies, qds_to_hys_order.get('curr_id', ''),
									snap_ids.get('batches_list_2', ''))
			self.check_batch_start(qds_cookies, qds_to_hys_order.get('curr_id', ''),
								   snap_ids.get('batches_list_2', ''), files)

			snap_ids = self.split_snap_id(hys_cookies,hys_to_scs_order.get('curr_id', ''), '发货')
			self.check_batch_middle(hys_cookies,hys_to_scs_order.get('curr_id', ''),
									snap_ids.get('batches_list_1', ''))
			self.check_batch_middle(hys_cookies,hys_to_scs_order.get('curr_id', ''),
									snap_ids.get('batches_list_2', ''))


			"""渠道商批次付款"""
			if qds_to_hys_payrate_id[2]:
				qds_to_hys_batch = self.batch_googs_pay(qds_cookies, qds_to_hys_order.get('curr_id', ''), '到货分批')

				"""华元素批次收款-付款"""
				self.batch_shoukuan(hys_cookies, qds_to_hys_batch)
			if hys_to_scs_payrate_id[2]:
				hys_to_scs_batch = self.batch_googs_pay(hys_cookies, hys_to_scs_order.get('curr_id', ''), '到货分批')

				"""生产商批次收款-付款"""
				self.batch_shoukuan(scs_cookies, hys_to_scs_batch)

		else:
			if qds_to_hys_payrate_id[1]:
				pay_way=self.balance_or_pay(qds_cookies, qds_to_hys_order.get('发货款', '').get('curr_pay_id', ''),
									qds_to_hys_order.get('发货款', '').get('amount', ''))

				self.shoukuan_pay(hys_cookies, qds_to_hys_order.get('发货款', '').get('curr_pay_id', ''),
								  qds_to_hys_order.get('发货款', '').get('amount', ''),pay_way)
			if hys_to_scs_payrate_id[1]:
				pay_way=self.balance_or_pay(hys_cookies, hys_to_scs_order.get('发货款', '').get('curr_pay_id', ''),
									hys_to_scs_order.get('发货款', '').get('amount', ''))

				self.shoukuan_pay(scs_cookies, hys_to_scs_order.get('发货款', '').get('curr_pay_id', ''),
								  hys_to_scs_order.get('发货款', '').get('amount', ''),pay_way)

			print('----------生产商一次发货----------')
			snap_id_fahuo = self.get_goods_information(scs_cookies, hys_to_scs_order['curr_id'])
			dict_keys = ['hegezheng']
			files = self.get_img(dict_keys)
			self.right_goods(scs_cookies, snap_id_fahuo, hys_to_scs_order['curr_id'])
			self.delivery_goods(scs_cookies, hys_to_scs_order['curr_id'], files)

			print('----------到货验收----------')
			snap_id_yanshou = self.ckeck_goods_information(qds_cookies, qds_to_hys_order['curr_id'])
			self.right_check_goods(qds_cookies, snap_id_yanshou, qds_to_hys_order['curr_id'])
			dict_keys = ['yanshou']
			files = self.get_img(dict_keys)
			self.check_goods(qds_cookies, qds_to_hys_order['curr_id'], files)

			self.orderinfo_check_goods(hys_cookies, hys_to_scs_order['curr_id'])

			if qds_to_hys_payrate_id[2]:
				print('----------付到货款----------')
				pay_way=self.balance_or_pay(qds_cookies, qds_to_hys_order.get('到货款', '').get('curr_pay_id', ''),
									qds_to_hys_order.get('到货款', '').get('amount', ''))

				self.shoukuan_pay(hys_cookies, qds_to_hys_order.get('到货款', '').get('curr_pay_id', ''),
								  qds_to_hys_order.get('到货款', '').get('amount', ''),pay_way)
			if hys_to_scs_payrate_id[2]:
				pay_way=self.balance_or_pay(hys_cookies, hys_to_scs_order.get('到货款', '').get('curr_pay_id', ''),
									hys_to_scs_order.get('到货款', '').get('amount', ''))

				self.shoukuan_pay(scs_cookies, hys_to_scs_order.get('到货款', '').get('curr_pay_id', ''),
								  hys_to_scs_order.get('到货款', '').get('amount', ''),pay_way)

		print('----------安装----------')
		dict_keys = ['hegezheng']
		files = self.get_img(dict_keys)
		self.install_goods(scs_cookies, hys_to_scs_order['curr_id'], files)
		self.install_goods(hys_cookies, qds_to_hys_order['curr_id'], files)

		print('----------安装验收----------')
		dict_keys = ['hegezheng', 'ff1']
		files = self.get_img(dict_keys)
		self.check_install(qds_cookies, qds_to_hys_order['curr_id'], files)
		self.check_install(hys_cookies, hys_to_scs_order['curr_id'])

		if qds_to_hys_payrate_id[3]:
			print('----------收付安装款----------')
			pay_way=self.balance_or_pay(qds_cookies, qds_to_hys_order.get('安装款', '').get('curr_pay_id', ''),
								qds_to_hys_order.get('安装款', '').get('amount', ''))

			self.shoukuan_pay(hys_cookies, qds_to_hys_order.get('安装款', '').get('curr_pay_id', ''),
							  qds_to_hys_order.get('安装款', '').get('amount', ''),pay_way)
		if hys_to_scs_payrate_id[2]:
			pay_way=self.balance_or_pay(hys_cookies, hys_to_scs_order.get('安装款', '').get('curr_pay_id', ''),
								hys_to_scs_order.get('安装款', '').get('amount', ''))

			self.shoukuan_pay(scs_cookies, hys_to_scs_order.get('安装款', '').get('curr_pay_id', ''),
							  hys_to_scs_order.get('安装款', '').get('amount', ''),pay_way)

		print('----------结算验收----------')
		self.account_check(scs_cookies, hys_to_scs_order['curr_id'])
		self.account_check(hys_cookies, qds_to_hys_order['curr_id'])

		if qds_to_hys_payrate_id[4]:
			print('----------收付结算款----------')
			pay_way=self.balance_or_pay(qds_cookies, qds_to_hys_order.get('结算款', '').get('curr_pay_id', ''),
								qds_to_hys_order.get('结算款', '').get('amount', ''))

			self.shoukuan_pay(hys_cookies, qds_to_hys_order.get('结算款', '').get('curr_pay_id', ''),
							  qds_to_hys_order.get('结算款', '').get('amount', ''),pay_way)
		if hys_to_scs_payrate_id[4]:
			pay_way=self.balance_or_pay(hys_cookies, hys_to_scs_order.get('结算款', '').get('curr_pay_id', ''),
								hys_to_scs_order.get('结算款', '').get('amount', ''))

			self.shoukuan_pay(scs_cookies, hys_to_scs_order.get('结算款', '').get('curr_pay_id', ''),
							  hys_to_scs_order.get('结算款', '').get('amount', ''),pay_way)

		print('----------质保结束----------')
		dict_keys = ['hegezheng']
		files = self.get_img(dict_keys)
		self.complete_insurance(scs_cookies, hys_to_scs_order['curr_id'], files)
		self.complete_insurance(hys_cookies, qds_to_hys_order['curr_id'], files)

		if qds_to_hys_payrate_id[5]:
			print('----------收付质保金----------')
			pay_way=self.balance_or_pay(qds_cookies, qds_to_hys_order.get('质保金', '').get('curr_pay_id', ''),
								qds_to_hys_order.get('质保金', '').get('amount', ''))

			self.shoukuan_pay(hys_cookies, qds_to_hys_order.get('质保金', '').get('curr_pay_id', ''),
							  qds_to_hys_order.get('质保金', '').get('amount', ''),pay_way)
		if hys_to_scs_payrate_id[5]:
			pay_way=self.balance_or_pay(hys_cookies, hys_to_scs_order.get('质保金', '').get('curr_pay_id', ''),
								hys_to_scs_order.get('质保金', '').get('amount', ''))

			self.shoukuan_pay(scs_cookies, hys_to_scs_order.get('质保金', '').get('curr_pay_id', ''),
							  hys_to_scs_order.get('质保金', '').get('amount', ''),pay_way)

	"""智能招标"""
	def start_bidding(self,is_stop=None):
		print('----------智能招标流程----------')
		# self.get_mysql_name()
		user={'other': 'SKS123', 'account_type': 3}
		changshang_bidding_cookies = self.login_swith_company(user['other'],user['account_type'])

		headers = self.huayuansu_cookies
		members = self.crete_bidding(headers)
		if is_stop=='发标':
			return
		for member in members:
			self.approve_bidding(member, '发标')
		self.bindding_information(headers)
		headers = self.changshang_cookies
		self.submite_approve_for_bidding(headers)
		headers = changshang_bidding_cookies
		self.submite_approve_for_bidding(headers)
		headers = self.huayuansu_cookies
		tender_informations = self.approve_author(headers)
		self.appove_for_tender(tender_informations)
		headers = self.changshang_cookies
		self.bidding_product(headers)
		headers = changshang_bidding_cookies
		self.bidding_product(headers)
		headers = self.huayuansu_cookies
		members = self.back_bidding(headers)
		for member in members:
			self.approve_bidding(member, '回标')
		members = self.min_price_approve(headers)
		for member in members:
			self.approve_bidding(member, '最低价')
		members = self.evaluate_bidding(headers)
		for member in members:
			self.approve_bidding(member, '评标')
		self.discuss_bidding(headers)
		headers = changshang_bidding_cookies
		self.change_price(headers)
		headers = self.changshang_cookies
		self.change_price(headers)
		headers = self.huayuansu_cookies
		members = self.compare_change_price(headers)
		self.prove_change_bidding(members)
		members = self.sure_bidding(headers)
		for member in members:
			self.approve_bidding(member, '定标')
		self.sign_bidding(headers)

	"""上下游充值"""
	def pay_cash(self,companys):
		print('----------上下游充值收付款----------')
		headers=self.shigongfang_cookies
		cash_information=self.down_recharge_cash(headers,companys['hualifang']['company_name'])
		headers=self.hualifang_cookies
		new_cash_information=self.up_recharge_cash(headers,cash_information,companys['huayuansu']['company_name'])
		headers=self.huayuansu_cookies
		final_cash_information=self.up_recharge_cash(headers,new_cash_information,companys['changshang']['company_name'])
		headers=self.changshang_cookies
		self.up_recharge_cash(headers,final_cash_information)

	"""询价报价"""
	def up_down_inquiry(self):
		headers=self.shigongfang_cookies
		sheet_information=self.add_down_inquiry(headers)
		headers=self.hualifang_cookies
		self.add_up_inquiry(headers,sheet_information)
		headers=self.huayuansu_cookies
		self.add_up_inquiry(headers, sheet_information)
		headers=self.changshang_cookies
		self.add_up_inquiry(headers, sheet_information,mode=1)

	def try_alone_api(self,user):
		headers=self.get_headers(user)
		sheet_id=self.notice_info(headers,660)

	def print_error(self,value):
		print(value)

class Klass(object):
	host='http://192.168.188.14:10157'
	users={
		'shigongfang': {'fuzheren': 'caoyuehua', 'account_type': 5,'company_name':'河南平安实业有限公司','company_id':174},
		'hualifang': {'fuzheren': '13418911156', 'caiwu': 'wangjialehys1', 'dingdan': 'chengzhefeng', 'shenpi': 'monica',
					  'account_type': 1,'company_name':'深圳市华立方商业集团有限公司','company_id':33},
		'qudaoshang': {'fuzheren': 'houdong', 'account_type': 4,'company_name':'河南浩海商贸有限公司','company_id':153},
		'huayuansu': {'fuzheren': 'duanye', 'caiwu': 'wangjialehys1', 'dingdan': 'wangjialehys1', 'shenpi': 'monica',
					  'account_type': 2,'company_name':'华元素采购（深圳）有限公司','company_id':34},
		'changshang': {'fuzheren': 'nuobeier', 'other': 'SKS123', 'account_type': 3,'company_name':'杭州诺贝尔陶瓷有限公司','company_id':86}
	}
	def __init__(self):
		print("Constructor ... %s" % multiprocessing.current_process().name)

	def __del__(self):
		print("... Destructor %s" % multiprocessing.current_process().name)

	def __call__(self, host,users):
		return self.func(host,users)

	def func(self,host,users):
		pp=Use_modle(host)
		pp.set_cookies(users)
		pp.start_bidding()

	def run(self,num=10):
		pool = multiprocessing.Pool()
		for num in range(num):
			pool.apply_async(self.func,args=(host,users,))
		pool.close()
		pool.join()

if __name__ == '__main__':
	host = 'http://dev.echronos.com:10460'
	users_information = {
		'shigongfang': {'fuzheren': 'caoyuehua', 'account_type': 5,'company_name':'河南平安实业有限公司','company_id':174},
		'hualifang': {'fuzheren': '13418911156', 'caiwu': 'wangjialehys1', 'dingdan': 'chengzhefeng', 'shenpi': 'monica',
					  'account_type': 1,'company_name':'深圳市华立方商业集团有限公司','company_id':33},
		'qudaoshang': {'fuzheren': 'houdong', 'account_type': 4,'company_name':'河南浩海商贸有限公司','company_id':153},
		'huayuansu': {'fuzheren': 'duanye', 'caiwu': 'wangjialehys1', 'dingdan': 'wangjialehys1', 'shenpi': 'monica',
					  'account_type': 2,'company_name':'华元素采购（深圳）有限公司','company_id':34},
		'changshang': {'fuzheren': 'nuobeier', 'other': 'SKS123', 'account_type': 3,'company_name':'杭州诺贝尔陶瓷有限公司','company_id':86}
	}
	aq=[100, 0, 0, 0, 0, 0]
	sale_id={'product_id_1': 846248, 'product_id_2': 846250}
	payrate_ids={'changshang_to_huayuansu':aq,
				 'huayuansu_to_hualifang': aq,
				 'hualifang_to_shigongfang': aq,
				 'hualifang_to_qudaoshang': aq,
				 'huayuansu_to_qudaoshang': aq}
	scales = {'changshang_to_huayuansu': 80,
			  'huayuansu_to_hualifang': 85,
			  'huayuansu_to_qudaoshang':85,
			  'hualifang_to_shigongfang': 90}
	names_company = '汽车服务'
	order_status=['生产商发货完成','施工方发货验收完成','华立方到货验收完成','华元素到货验收完成']
	process=Use_modle(host)
	process.set_cookies(users_information)
	"""注册新用户-公司认证-审批"""
	# process.prove_company(names_company)
	# """添加成员-授予权限"""
	# phone=process.add_personal_give_roles(users_information)
	phone=['13412231740', '13512231740', '13612231741', '13712231741', '13812231741']
	users = {
		'shigongfang': {'fuzheren': phone[0], 'account_type': 5, 'company_name': '河南平安实业有限公司', 'company_id': 174},
		'hualifang': {'fuzheren': phone[1], 'caiwu': 'wangjialehys1', 'dingdan': 'chengzhefeng',
					  'shenpi': 'monica',
					  'account_type': 1, 'company_name': '深圳市华立方商业集团有限公司', 'company_id': 33},
		'qudaoshang': {'fuzheren': phone[2], 'account_type': 4, 'company_name': '河南浩海商贸有限公司', 'company_id': 153},
		'huayuansu': {'fuzheren': phone[3], 'caiwu': 'wangjialehys1', 'dingdan': 'wangjialehys1', 'shenpi': 'monica',
					  'account_type': 2, 'company_name': '华元素采购（深圳）有限公司', 'company_id': 34},
		'changshang': {'fuzheren': phone[4], 'other': 'SKS123', 'account_type': 3, 'company_name': '杭州诺贝尔陶瓷有限公司',
					   'company_id': 86}
	}
	# process.set_cookies(users)
	# """批量上架商品-设置圈层价：战采"""
	# process.upload_goods_to_circle(scales, users,payrate_ids,catelog_id=622,price=200)
	# """批量上架商品-设置圈层价：渠道"""
	# process.upload_goods_channel(scales, users,payrate_ids)
	"""战采：订单流程：是否经过商户(0为不通过）"""
	# process.only_order_process(sale_id,payrate_ids,condition=0)
	# process.only_order_process(sale_id,payrate_ids,condition=1)
	"""战采：订单全流程：是否分批（0为不分批）"""
	for order_statu in order_status:
		try:
			# process.all_order_process(sale_id,payrate_ids,condition=0,is_stop=order_statu)
			process.all_order_process(sale_id,payrate_ids,condition=1,is_stop=order_statu)
		except:
			continue
	# """渠道、特殊战采流程(batch:0为不分批,condition:2为渠道）"""
	# process.channel_order_process(sale_id,payrate_ids,batch=1,condition=2)
	# process.channel_order_process(sale_id,payrate_ids,batch=0,condition=1)
	# """智能招标"""
	# process.start_bidding()
	# th=threading.Thread
	# for i in range(1):
	# 	t1=th(target=process.start_bidding)
	# 	t2=th(target=process.pay_cash,args=(users,))
	# t1.start()
	# t2.start()
	# t1.join()
	# t2.join()
	# pool=Pool()
	# for i in range(8):
	# 	pool.apply_async(func=process.start_bidding,error_callback=process.print_error)
	# pool.close()
	# pool.join()
	# threadPool = ThreadPoolExecutor(max_workers=4, thread_name_prefix="test_")
	# locks=threading.Lock()
	# for i in range(0,10):
	# 	future = threadPool.submit(process.start_bidding,locks)
	# threadPool.shutdown(wait=True)
	# """账户充值收款"""
	# process.pay_cash(users)
	# """询价报价"""
	# process.up_down_inquiry()
	# process.try_alone_api('wechat20190126045047')
	# process.gets_mysql_names()
	# phone_nums=process.get_phonenum(100)
	# for i in phone_nums:
	# 	try:
	# 		pool.apply_async(func=process.sign_in,args=(i,),error_callback=process.print_error)
	# 	except Exception as e:
	# 		print(f'第{i}次创建失败',e)
	# pool.close()
	# pool.join()
	# _aa=Klass()
	# _aa.run()
