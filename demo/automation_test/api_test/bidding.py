# -*- coding:utf-8 -*-
import json
import time,datetime,traceback
import requests
import os
from jsonpath import jsonpath
from automation_test import conn_mysql
from automation_test.api_test.login_information import Login_envirment

class Bidding():

	def __init__(self, host):
		self.session = requests.Session()
		self.environment = host

	def get_json_path(self, result, json_value):
		# 获取json的jsonpath
		try:
			list_paths = []
			json_name = jsonPath.get_path(result, "$", json_value)
			print(json_name[0])
		except:
			print("未获取到对于的jsonpath")

	def file_param(self, dict_key):
		img_path = f"{os.path.dirname(os.path.abspath(__file__))}/123.jpg"
		with open(f"{img_path}", "rb") as f:
			img = f.read()
		file = {dict_key: ("123.jpg", img)}
		return file

	def send_request(self, method, url_1, headers, params={}, files={}, bytes={},status="form-data"):
		try:
			url = f"{self.environment}{url_1}"
			if method == "get":
				response = self.session.get(url, headers=headers["header"], params=params, files=files)

			else:
				if status == "form-data":
					response = self.session.post(url, headers=headers["header"], data=params, files=files)
				elif status == "special":
					response = self.session.post(url, headers=headers["header"], data=params, bytes=bytes)
				else:
					response = self.session.post(url, headers=headers["header"], json=params, files=files)


			if response.json()['errcode']==0:
				print(response.status_code, response.json())
				if files:
					time.sleep(1)
			#
			# else:
			# 	response=self.send_request(method, url, headers, params={}, files={}, bytes={}, status="form-data")

			return response
		except Exception as exc:
			print(exc)
			print(traceback.format_exc())

	def get_headers(self, username):
		# 获取 headers
		host=self.environment
		rr = Login_envirment(host)
		headers = rr.get_login_token(username)
		return headers

	def get_datatime(self):
		threeDayAgo = datetime.datetime.today() - datetime.timedelta(2)
		otherStyleTime = threeDayAgo.strftime("%m%d")
		return otherStyleTime

	def get_mysql_name(self):
		host = '192.168.188.12'
		db = ''
		sql_data = "show databases"
		baocun = conn_mysql.Operation_mysql().get_information(sql_data, host, db)
		print(baocun)
		for i in range(8):
			threeDayAgo = datetime.datetime.today() - datetime.timedelta(i)
			otherStyleTime_1 = threeDayAgo.strftime("%Y%m%d")
			mysql_name = f'epodb_{otherStyleTime_1}'
			if mysql_name in baocun:
				self.set_mysql_name(mysql_name)

	def set_mysql_name(self,names):
		self.mysql_name=names

	def get_login_name(self,member_id):
		host = '192.168.188.12'
		data_db='epodb_20201108'
		sql=f'SELECT login_name from backend_member where `id`={member_id};'
		mysql_test=conn_mysql.Operation_mysql().get_information(sql, host, data_db)
		# print(mysql_test[0])
		return mysql_test[0]

	def set_bidding_id(self,bidding_id):
		self.bidding_id=bidding_id

	def set_payrate_id(self,payrate_id):
		self.payrate_id=payrate_id

	def set_catelog_id(self,catelog_id):
		self.catelog_id=catelog_id

	""""创建智能招标单"""
	def crete_bidding(self,headers,catelog_id=622):
		self.set_catelog_id(catelog_id)
		url_1=f'/bk/qtd/issue/sheet/create/'
		response1=self.send_request('post',url_1,headers)
		self.set_bidding_id(response1.json()['data']['id'])
		# self.bidding_ids(134)

		"""填写招标信息"""
		url_2=f'/bk/qtd/issue/sheet/info/{self.bidding_id}'
		end_time=int(time.time())+700000
		body={'title':f'测试数据{self.bidding_id}','project_name':'测试智能招标数据','end_time':end_time,'comment':'测试数据007'}
		response2=self.send_request('post',url_2,headers,params=body)

		"""上传招标图片"""
		url_3=f'/bk/qtd/issue/sheet/announcement/{self.bidding_id}?format=json'
		body={'type':'announcement_file','action':'add'}
		files=self.file_param('attachment') # 图片：招标公告(盖章版)
		response3=self.send_request('post',url_3,headers,params=body,files=files)

		body = {'type': 'invitation_file', 'action': 'add'} # 图片：招标邀请函(盖章版)
		response3 = self.send_request('post', url_3, headers, params=body, files=files)

		body = {'type': 'bid_file', 'action': 'add'} # 图片：招标文件(盖章版)
		response3 = self.send_request('post', url_3, headers, params=body, files=files)

		body = {'type': 'spec_file', 'action': 'add'} # 图片：招标技术标准
		response3 = self.send_request('post', url_3, headers, params=body, files=files)

		body = {'type': 'other_file', 'action': 'add'} # 图片：其他附件
		response3 = self.send_request('post', url_3, headers, params=body, files=files)
		response3 = self.send_request('post', url_3, headers, params=body, files=files)

		body = {'type': 'announcement_content', 'action': 'add','content':'<p>测试数据007</p>'} # 文本框：备注信息
		response3=self.send_request('post',url_3,headers,params=body)

		"""提交招标信息"""
		url_4=f'/bk/qtd/sheet/dostep/{self.bidding_id}'
		body={'curr_step':'qtd_status_issue_announcement'}
		response4=self.send_request('post',url_4,headers,params=body)

		"""获取商品分类信息"""
		url_5=f'/bk/product_name/onsale/metas/{self.catelog_id}'
		response5=self.send_request('get',url_5,headers)
		detail_1=jsonpath(response5.json(),'$.data.name_list[0].detail_list[0].detail_id')
		detail_2=jsonpath(response5.json(),'$.data.spec_list[0].detail_list[0].detail_id')
		detail_3=jsonpath(response5.json(),'$.data.spec_list[0].detail_list[1].detail_id')

		"""添加招标商品"""
		url_6=f'/bk/qtd/issue/sheet/inquiry/add/{self.bidding_id}?format=json'
		body={'catelog_id':self.catelog_id,'meta_ids':[detail_1,detail_2,detail_3],'unit':'箱'}
		response6=self.send_request('post',url_6,headers,params=body)
		time.sleep(3)

		"""提交发标评审"""
		url_7=f'/bk/qtd/sheet/dostep/{self.bidding_id}'
		body={'curr_step':'qtd_status_issue_details'}
		response7=self.send_request('post',url_7,headers,params=body)

		"""获取发标评审人员名单"""
		url_8=f'/bk/qtd/issue/sheet/approval/{self.bidding_id}?format=json'
		response8=self.send_request('get',url_8,headers)
		results=response8.json()['data']['flows'][0]['stages']
		members=[]
		for result in results:
			for i in result:
				if i['type']=='member':
					members.append({'name':i['title'],'id':i['id'],'approver_id':i['approver_id'],'level':i['level']})
		print('华元素审批人员信息：',members)
		return members

	"""华元素通过审批"""
	def approve_bidding(self,member,condition):
		"""从数据库查询审批人员登录名"""
		login_name=self.get_login_name(member['id'])
		headers=self.get_headers(login_name)

		"""通过发标审批"""
		if condition=='发标':
			url=f'/bk/qtd/issue/sheet/approval/{self.bidding_id}?format=json'
		elif condition=='回标':
			url=f'/bk/qtd/return/approval/{self.bidding_id}?format=json'
		elif condition=='最低价':
			url=f'/bk/qtd/eval/price/lowest/approval/{self.bidding_id}?format=json'
		elif condition=='评标':
			url=f'/bk/qtd/eval/tenders/approval/{self.bidding_id}?format=json'
		elif condition=='定标':
			url=f'/bk/qtd/scaling/companys/approval/{self.bidding_id}?format=json'
		body={'action':'approve','content':'同意','approver_id':member['approver_id']}
		response=self.send_request('post',url,headers,params=body)

	"""查看招标信息"""
	def bindding_information(self,headers):

		url_1=f'/bk/qtd/issue/sheet/info/{self.bidding_id}?format=json'
		response1=self.send_request('get',url_1,headers)

		url_2=f'/bk/qtd/issue/sheet/approval/{self.bidding_id}?format=json'
		response2=self.send_request('get',url_2,headers)

		url_3=f'/bk/qtd/issue/sheet/info/{self.bidding_id}?format=json'
		response3=self.send_request('get',url_3,headers)

	"""生产商提交资质评审"""
	def submite_approve_for_bidding(self,headers):
		"""获取标书ID"""
		url_4=f'/bk/qtd/sheet/list/tender/?format=json&page=1&page_size=10&key=&status=all'
		response4=self.send_request('get',url_4,headers)

		# url_5=f'/bk/product_name/onsale/com/brands/{company_id}?format=json'
		# response5=self.send_request('get',url_5,headers)

		"""获取提交标书sheet_id"""
		url_1=f'/bk/qtd/tender/main/{self.bidding_id}?format=json'
		response1=self.send_request('get',url_1,headers)
		sheet_id=response1.json()['data']['id']

		"""上传投标附件"""
		url_2=f'/bk/qtd/tender/authentication/{sheet_id}?format=json'
		body={'type':'invitation_receipt_file','action':'add'}
		files=self.file_param('attachment') # 投标邀请函回执
		response2=self.send_request('post',url_2,headers,params=body,files=files)

		body = {'type': 'commitment_file', 'action': 'add'}
		files = self.file_param('attachment')  # 投标承诺函
		response2 = self.send_request('post', url_2, headers, params=body, files=files)

		body = {'type': 'spec_response_file', 'action': 'add'}
		files = self.file_param('attachment')  # 技术标准响应表
		response2 = self.send_request('post', url_2, headers, params=body, files=files)

		body = {'type': 'other_file', 'action': 'add'}
		files = self.file_param('attachment')  # 资质文件
		response2 = self.send_request('post', url_2, headers, params=body, files=files)

		"""提交资质评审"""
		url_3=f'/bk/qtd/tender/authentication/{sheet_id}?format=json'
		body={'type':'submit','action':'modify'}
		response3=self.send_request('post',url_3,headers,params=body)

	"""华元素提交厂家资质评审"""
	def approve_author(self,headers):
		"""获取厂家资质ID"""
		url_1=f'/bk/qtd/return/auth/tenders/{self.bidding_id}?page=1&page_size=999&format=json'
		response1=self.send_request('get',url_1,headers)
		tender_id_1=response1.json()['data'][0]['id']
		tender_id_2=response1.json()['data'][1]['id']

		"""招标人通过资质评审"""
		url_2=f'/bk/qtd/return/auth/tender/{tender_id_1}?format=json'
		body={'action':'approve','content':'测试数据007'}
		response2=self.send_request('post',url_2,headers,params=body)
		tender_ids_1=[]
		for tender_id in response2.json()['data']['stages']:
				for i in tender_id:
					if i['type'] == 'member':
						tender_ids_1.append({'name': i['title'], 'id': i['id'], 'approver_id': i['approver_id'], 'level': i['level']})

		url_3 = f'/bk/qtd/return/auth/tender/{tender_id_2}?format=json'
		body = {'action': 'approve', 'content': '测试数据007'}
		response3 = self.send_request('post', url_3, headers, params=body)
		tender_ids_2 = []
		for tender_id in response3.json()['data']['stages']:
			for i in tender_id:
				if i['type'] == 'member':
					tender_ids_2.append({'name': i['title'], 'id': i['id'], 'approver_id': i['approver_id'], 'level': i['level']})
		tender_ids={tender_id_1:tender_ids_1,tender_id_2:tender_ids_2}
		print(tender_ids)
		return tender_ids

	"""华元素审批厂家资质"""
	def appove_for_tender(self,tender_informations):
		for tender_information in tender_informations:
			tender_id=tender_information
			for member in tender_informations[tender_information]:
				member_id=member['id']
				user=self.get_login_name(member_id)
				headers=self.get_headers(user)
				approve_id=member['approver_id']
				url=f'/bk/qtd/return/auth/tender/{tender_id}?format=json'
				body={'action':'approve','content':'测试数据007','approver_id':approve_id}
				response=self.send_request('post',url,headers,params=body)

	"""厂家投标"""
	def bidding_product(self,headers):
		"""获取投标ID"""
		url_1=f'/bk/qtd/tender/main/{self.bidding_id}?format=json'
		response1=self.send_request('get',url_1,headers)
		tender_id=response1.json()['data']['id']

		"""查看资质评审状态"""
		url_13 = f'/bk/qtd/tender/auth/confirm/{tender_id}?format=json'
		body = {'action': 'confirm'}
		response13 = self.send_request('post', url_13, headers, params=body)

		"""获取投标产品报价ID"""
		url_2=f'/bk/qtd/tender/sales/prices/{tender_id}?page=1&page_size=1&format=json'
		response2=self.send_request('get',url_2,headers)
		product_ids=jsonpath(response2.json(),'$.data.quotations[0][0]')
		quotation_ids=[]
		for i in product_ids:
			for j in i:
				quotation_ids.append(i[j]['quotation_id'])

		"""生产商上传附件"""
		url_2_1=f'/bk/qtd/tender/files/'
		body={'tender_id':tender_id,'action':'add'}
		files = self.file_param('file')
		for i in range(2):
			response2 = self.send_request('post', url_2_1, headers,params=body,files=files)

		"""设置产品价格"""
		url_3=f'/bk/qtd/tender/sales/prices/{tender_id}?format=json'
		body_1={'action':'modify','market_price':200,'quotation_ids':quotation_ids[0]}
		body_2={'action':'modify','market_price':300,'quotation_ids':quotation_ids[1]}
		body_3={'action':'modify','discount':90,'quotation_ids':quotation_ids[0]}
		body_4={'action':'modify','discount':90,'quotation_ids':quotation_ids[1]}
		response3=self.send_request('post',url_3,headers,params=body_1)
		response3=self.send_request('post',url_3,headers,params=body_2)
		response3=self.send_request('post',url_3,headers,params=body_3)
		response3=self.send_request('post',url_3,headers,params=body_4)

		"""获取投标产品销售单元ID"""
		url_3= f'/bk/qtd/tender/sales/skumoq/{tender_id}?page=1&page_size=1&format=json'
		response3 = self.send_request('get', url_3, headers)
		product_ids = response3.json()['data']['sku_moq']
		sale_ids = []
		for i in product_ids:
			sale_ids.append(product_ids[i]['sale_id'])

		"""设置投标产品销售单元"""
		url_4 = f'/bk/qtd/tender/sales/skumoq/{tender_id}?format=json'
		body_1 = {'action': 'modify', 'moq': 10, 'sale_ids': sale_ids[0]}
		body_2 = {'action': 'modify', 'moq': 10, 'sale_ids': sale_ids[1]}
		body_3 = {'action': 'modify', 'sku': 1, 'sale_ids': sale_ids[0]}
		body_4 = {'action': 'modify', 'sku': 1, 'sale_ids': sale_ids[1]}
		response3 = self.send_request('post', url_4, headers, params=body_1)
		response3 = self.send_request('post', url_4, headers, params=body_2)
		response3 = self.send_request('post', url_4, headers, params=body_3)
		response3 = self.send_request('post', url_4, headers, params=body_4)

		"""获取投标产品运费模板ID"""
		url_5=f'/bk/product_name/onsale/com/transports/?format=json'
		response5=self.send_request('get',url_5,headers)
		transport_id=response5.json()['data'][0]['transport_template_id']

		"""设置投标产品运费模板"""
		url_6=f'/bk/qtd/tender/sales/transport/{tender_id}?format=json'
		body_1={'action':'modify','sale_ids':sale_ids[0],'transport_id':transport_id}
		body_2={'action':'modify','sale_ids':sale_ids[1],'transport_id':transport_id}
		response6=self.send_request('post',url_6,headers,params=body_1)
		response6=self.send_request('post',url_6,headers,params=body_2)

		"""设置投标产品图片"""
		url_7=f'/bk/qtd/tender/sales/images/{tender_id}?format=json'
		files=self.file_param('image')
		body_1={'action':'add','sale_ids':sale_ids[0]}
		body_2={'action':'add','sale_ids':sale_ids[1]}
		response7=self.send_request('post',url_7,headers,params=body_1,files=files)
		response7=self.send_request('post',url_7,headers,params=body_2,files=files)

		"""获取商品详情模板ID"""
		try:
			url_8=f'/bk/product_name/onsale/sale/template/details/list/{self.catelog_id}?format=json'
			response8=self.send_request('get',url_8,headers)
			template_id=response8.json()['data'][0]['id']
		except:
			url_11=f'/bk/product_name/onsale/sale/template/details/create/{self.catelog_id}?format=json'
			body={'format':'json'}
			response11=self.send_request('post',url_11,headers,params=body)
			template_id=response11.json()['data']['id']

			url_12=f'/bk/product_name/onsale/sale/template/details/edit/{template_id}'
			body= {'type': 'image','action': 'add'}
			files=self.file_param('image')
			response12=self.send_request('post',url_12,headers,params=body,files=files)

		"""设置商品详情模板"""
		url_9=f'/bk/qtd/tender/sales/details/{tender_id}?format=json'
		body={'template_id':template_id,'action':'add','catelog_id':{self.catelog_id}}
		response9=self.send_request('post',url_9,headers,params=body)
		time.sleep(2)

		"""提交投标"""
		url_10=f'/bk/qtd/tender/quotations/sumbit/{tender_id}?format=json'
		body={'action':'submit'}
		response10=self.send_request('post',url_10,headers,params=body)

	"""华元素发起回标审批"""
	def back_bidding(self,headers):
		"""获取投标信息"""
		url_1=f'/bk/qtd/return/tenders/round/{self.bidding_id}?page=1&page_size=999&format=json'
		response1=self.send_request('get',url_1,headers)

		"""发起回标审批"""
		url_2=f'/bk/qtd/return/tenders/{self.bidding_id}?format=json'
		body={'comment':'测试数据007','action':'start_eval'}
		response2=self.send_request('post',url_2,headers,params=body)

		"""获取回标审批人员"""
		url_3=f'/bk/qtd/return/approval/{self.bidding_id}?format=json'
		response3=self.send_request('get',url_3,headers)
		tender_ids_1 = []
		for tender_id in response3.json()['data']['flows'][0]['stages']:
			for i in tender_id:
				if i['type'] == 'member':
					tender_ids_1.append({'name': i['title'], 'id': i['id'], 'approver_id': i['approver_id'], 'level': i['level']})
		return tender_ids_1

	"""提交最低价审批"""
	def min_price_approve(self,headers):
		"""触发评标"""
		url_4=f'/bk/qtd/return/approval/{self.bidding_id}?format=json'
		response4=self.send_request('get',url_4,headers)

		"""选择最低价"""
		url_3=f'/bk/qtd/eval/price/lowest/{self.bidding_id}?page=1&page_size=1&format=json'
		response3=self.send_request('get',url_3,headers)

		"""提交最低价审批"""
		url_1=f'/bk/qtd/eval/price/lowest/approval/{self.bidding_id}?format=json'
		body={'action':'start','content':'测试数据007'}
		response1=self.send_request('post',url_1,headers,params=body)

		"""获取最低价审批成员"""
		url_2=f'/bk/qtd/eval/price/lowest/approval/{self.bidding_id}?format=json'
		response2=self.send_request('get',url_2,headers)
		tender_ids_1 = []
		for tender_id in response2.json()['data']['flows'][0]['stages']:
			for i in tender_id:
				if i['type'] == 'member':
					tender_ids_1.append(
						{'name': i['title'], 'id': i['id'], 'approver_id': i['approver_id'], 'level': i['level']})
		return tender_ids_1

	"""提交评标审批"""
	def evaluate_bidding(self,headers):
		"""触发评标"""
		url_3=f'/bk/qtd/eval/price/lowest/approval/{self.bidding_id}?format=json'
		response3=self.send_request('get',url_3,headers)

		"""获取议标ID"""
		url_4=f'/bk/qtd/eval/tenders/{self.bidding_id}?format=json&page_size=999&page=1'
		response4=self.send_request('get',url_4,headers)
		sheet_id_1=response4.json()['data'][0]['id']
		sheet_id_2=response4.json()['data'][1]['id']

		"""选择议标类型"""
		url_5=f'/bk/qtd/eval/tender/content/{sheet_id_1}?format=json'
		response5=self.send_request('get',url_5,headers)

		url_5 = f'/bk/qtd/eval/tender/content/{sheet_id_2}?format=json'
		response5 = self.send_request('get', url_5, headers)

		"""提交评标审批"""
		url_1=f'/bk/qtd/eval/tenders/approval/{self.bidding_id}?format=json'
		body = {'action': 'start', 'content': '测试数据007'}
		response1=self.send_request('post',url_1,headers,params=body)

		"""获取评标成员"""
		url_2=f'/bk/qtd/eval/tenders/approval/{self.bidding_id}?format=json'
		response2 = self.send_request('get', url_2, headers)
		tender_ids_1 = []
		for tender_id in response2.json()['data']['flows'][0]['stages']:
			for i in tender_id:
				if i['type'] == 'member':
					tender_ids_1.append({'name': i['title'], 'id': i['id'], 'approver_id': i['approver_id'], 'level': i['level']})
		return tender_ids_1

	"""提交议标审批"""
	def discuss_bidding(self,headers):
		"""获取标书信息"""
		url_1=f'/bk/qtd/eval/tenders/approval/{self.bidding_id}?format=json'
		response1=self.send_request('get',url_1,headers)

		"""触发议标"""
		url_6 = f'/bk/qtd/discuss/progress/{self.bidding_id}?format=json'
		response6=self.send_request('get',url_6,headers)

		"""查看议标进度"""
		url_7 = f'/bk/qtd/discuss/negotiation/{self.bidding_id}?format=json'
		response2 = self.send_request('get', url_7, headers)

		"""获取议标ID"""
		url_2=f'/bk/qtd/discuss/negotiation/{self.bidding_id}?format=json'
		response2=self.send_request('get',url_2,headers)
		sheet_id_1=response2.json()['data'][0]['id']
		sheet_id_2=response2.json()['data'][1]['id']

		"""获取付款比例ID"""
		url_3=f'/orderinfo/circle/circle_payrate/?page=1&key='
		response3=self.send_request('get',url_3,headers)
		payrate_id=response3.json()['data']['payrates'][0]['id']
		self.set_payrate_id(payrate_id)

		"""选择付款比例"""
		url_4=f'/bk/qtd/discuss/negotiation/tender/payrate/{sheet_id_1}?format=json'
		body={'action':'add','catelog_id':self.catelog_id,'scaling_payrate_id':'','pay_rate_id':self.payrate_id}
		response4 = self.send_request('post', url_4, headers, params=body)

		url_4 = f'/bk/qtd/discuss/negotiation/tender/payrate/{sheet_id_2}?format=json'
		body = {'action': 'add', 'catelog_id': self.catelog_id, 'scaling_payrate_id': '', 'pay_rate_id': payrate_id}
		response4 = self.send_request('post', url_4, headers, params=body)

		"""上传议标记录"""
		url_5=f'/bk/qtd/discuss/negotiation/tender/records/{sheet_id_1}?format=json'
		body={'action':'add'}
		files=self.file_param('discuss_record')
		response5=self.send_request('post',url_5,headers,params=body,files=files)

		url_5 = f'/bk/qtd/discuss/negotiation/tender/records/{sheet_id_2}?format=json'
		body = {'action': 'add'}
		files = self.file_param('discuss_record')
		response5 = self.send_request('post', url_5, headers, params=body, files=files)

	"""厂家调价"""
	def change_price(self,headers):
		"""获取调价ID"""
		url_1=f'/bk/qtd/tender/main/{self.bidding_id}?format=json'
		response1=self.send_request('get',url_1,headers)
		sheet_id=response1.json()['data']['id']

		"""厂家完成调价"""
		url_2=f'/bk/qtd/tender/quotations/sumbit/{sheet_id}?format=json'
		body={'action':'submit'}
		response2=self.send_request('post',url_2,headers,params=body)

	"""调价完成，提交审批"""
	def compare_change_price(self,headers):
		"""获取调价ID"""
		url_1=f'/bk/qtd/discuss/negotiation/{self.bidding_id}?format=json'
		response1=self.send_request('get',url_1,headers)
		sheet_id_1=response1.json()['data'][0]['id']
		sheet_id_2=response1.json()['data'][1]['id']

		"""调价结束"""
		url_2=f'/bk/qtd/discuss/negotiation/tender/approval/{sheet_id_1}?format=json'
		body={'action':'approve','content':'测试数据007'}
		response2=self.send_request('post',url_2,headers,params=body)

		url_3 = f'/bk/qtd/discuss/negotiation/tender/approval/{sheet_id_2}?format=json'
		body = {'action': 'approve', 'content': '测试数据007'}
		response3 = self.send_request('post', url_3, headers, params=body)

		"""获取审批成员"""
		url_4=f'/bk/qtd/discuss/negotiation/scaling/info/{sheet_id_1}?format=json'
		response4=self.send_request('get',url_4,headers)
		members={}
		for tender_id in response4.json()['data']['flows'][0]['stages']:
			for i in tender_id:
				if i['type'] == 'member':
					members[sheet_id_1]={'name': i['title'], 'id': i['id'], 'approver_id': i['approver_id'], 'level': i['level']}

		url_5 = f'/bk/qtd/discuss/negotiation/scaling/info/{sheet_id_2}?format=json'
		response5 = self.send_request('get', url_5, headers)
		for tender_id in response5.json()['data']['flows'][0]['stages']:
			for i in tender_id:
				if i['type'] == 'member':
					members[sheet_id_2] = {'name': i['title'], 'id': i['id'], 'approver_id': i['approver_id'], 'level': i['level']}

		print(members)
		return members

	"""调价审批"""
	def prove_change_bidding(self,members):
		for member in members:
			login_name=self.get_login_name(members[member]['id'])
			headers=self.get_headers(login_name)

			"""通过调价审批"""
			url=f'/bk/qtd/discuss/negotiation/tender/approval/{member}?format=json'
			body={'action':'approve','content':'同意','approver_id':members[member]['approver_id']}
			response=self.send_request('post',url,headers,params=body)

	"""定标"""
	def sure_bidding(self,headers):
		"""触发定标"""
		url_1=f'/bk/qtd/issue/sheet/info/{self.bidding_id}?format=json'
		response1=self.send_request('get',url_1,headers)

		"""获取定标ID"""
		url_1 = f'/bk/qtd/discuss/negotiation/{self.bidding_id}?format=json'
		response1 = self.send_request('get', url_1, headers)
		sheet_id_1 = response1.json()['data'][0]['id']
		sheet_id_2 = response1.json()['data'][1]['id']

		"""分批定标"""
		url_2=f'/bk/qtd/scaling/companys/progress/{self.bidding_id}?format=json'
		body={'content':'测试数据007','scaling_ids':[sheet_id_1,sheet_id_2]}
		files=self.file_param('attach')
		response2=self.send_request('post',url_2,headers,params=body,files=files)

		"""获取定标审批成员"""
		url_3=f'/bk/qtd/scaling/companys/approval/{self.bidding_id}?format=json'
		response3=self.send_request('get',url_3,headers)
		members=[]
		for tender_id in response3.json()['data']['flows'][0]['stages']:
			for i in tender_id:
				if i['type'] == 'member':
					members.append({'name': i['title'], 'id': i['id'], 'approver_id': i['approver_id'], 'level': i['level']})
		return members

	"""签约"""
	def sign_bidding(self,headers):
		"""触发签约"""
		url_1=f'/bk/qtd/scaling/companys/approval/{self.bidding_id}?format=json'
		response1=self.send_request('get',url_1,headers)

		"""获取签约公司"""
		url_2=f'/bk/qtd/scaling/sales/sales/{self.bidding_id}?format=json'
		response2=self.send_request('get',url_2,headers)
		company_ids=[response2.json()['data'][0]['id'],response2.json()['data'][1]['id']]

		for company_id in company_ids:

			"""获取签约商品ID"""
			url_3=f'/bk/qtd/scaling/sales/tender/sales/{company_id}?format=json&page=1&page_size=9999&payment_id='
			response3=self.send_request('get',url_3,headers)
			sale_id_1=response3.json()['data'][0]['id']
			sale_id_2=response3.json()['data'][1]['id']

			"""签约"""
			url_4=f'/bk/qtd/scaling/sales/tender/sales/{company_id}?format=json'
			body={'action':'scaling','quotation_ids':[sale_id_1,sale_id_2]}
			response4=self.send_request('post',url_4,headers,params=body)

			"""上传战略合作协议"""
			url_5=f'/bk/qtd/contract/com/contracts/{company_id}?format=json'
			body={'action':'add','type':'contract_strategy'}
			files=self.file_param('contract')
			response5=self.send_request('post',url_5,headers,params=body,files=files)

			"""补充协议"""
			body = {'action':'add', 'type':'contract_replenish','payment_id':self.payrate_id}
			response5 = self.send_request('post', url_5, headers, params=body, files=files)

			"""商品上架"""
			url_5=f'/bk/qtd/scaling/sales/tender/onsale/{company_id}?format=json'
			body={'action':'onsale','quotation_ids':[sale_id_1,sale_id_2]}
			response5 = self.send_request('post', url_5, headers, params=body)

	def main_bidding(self):
		changshang_bidding_cookies = self.get_headers('SKS123')
		self.changshang_cookies=self.get_headers('caoyuehua')
		self.huayuansu_cookies=self.get_headers('duanye')
		scs_company1='21'
		scs_company2='86'

		headers = self.huayuansu_cookies
		members = self.crete_bidding(headers)
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

if __name__ == '__main__':
	host='http://dev.echronos.com:10460'
	test=Bidding(host)
	# headers=test.get_headers('13608141521')
	# test.submite_approve_for_bidding(headers)
	users = {
		'shigongfang': {'fuzheren': 'caoyuehua', 'account_type': 5},
		'hualifang': {'fuzheren': 'duanye', 'caiwu': 'wangjialehys1', 'dingdan': 'chengzhefeng', 'shenpi': 'monica',
					  'account_type': 1},
		'qudaoshang': {'fuzheren': 'houdong', 'account_type': 4},
		'huayuansu': {'fuzheren': 'duanye', 'caiwu': 'wangjialehys1', 'dingdan': 'wangjialehys1', 'shenpi': 'monica',
					  'account_type': 2},
		'changshang': {'fuzheren': 'nuobeier', 'other': 'SKS123', 'account_type': 3}
	}
	test.main_bidding()
	# headers=test.get_headers(users['huayuansu']['fuzheren'])
	# test.bidding_product(headers)
	# test.evaluate_bidding(headers)
	# test.discuss_bidding(headers)
	# test.compare_change_price(headers)
	# test.discuss_bidding(headers)
	# test.get_mysql_name()