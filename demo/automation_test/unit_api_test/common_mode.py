# -*- coding:utf-8 -*-
import requests
import pymysql
import os
import xlrd
import xlwt
import datetime
import jsonpath
import random
from enum import Enum
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class Constant(Enum):

	common_information=f'测试数据{random.randint(100,999)}'
	common_payrate_list=[100,0,0,0,0,0]

	common_sgf_role = '施工方'
	common_hlf_role = '华立方'
	common_qds_role= '渠道商'
	common_hys_role = '华元素'
	common_scs_role = '生产商'

	common_sgf_sign = 'caoyuehua'
	common_hlf_sign = 'zhangzihanghlf'
	common_qds_sign = 'houdong'
	common_hys_sign = 'duanye'
	common_scs_sign = 'nuobeier'

	common_sgf_company_name = '河南平安实业有限公司'
	common_hlf_company_name = '深圳市华立方商业集团有限公司'
	common_qds_company_name = '河南浩海商贸有限公司'
	common_hys_company_name = '华元素采购（深圳）有限公司'
	common_scs_company_name = '杭州诺贝尔陶瓷有限公司'

	common_sgf_company_type = 5
	common_hlf_company_type = 1
	common_qds_company_type = 4
	common_hys_company_type = 2
	common_scs_company_type = 3

	common_sgf_company_id = 174
	common_hlf_company_id = 33
	common_qds_company_id = 153
	common_hys_company_id = 34
	common_scs_company_id = 86

class CommonMethod():

	def __init__(self,environment):
		self.session=requests.Session()
		self.environment=environment

	def send_request(self,mothod,url,headers,body={},files=[],parame_type='form-data'):
		try:
			url = f"{self.environment}{url}"
			if mothod=='get':
				response=self.session.get(url,headers=headers['header'])

			else:
				if parame_type=='form-data':
					response=self.session.post(url,headers=headers['header'],data=body,files=files)
				else:
					response=self.session.post(url,headers=headers['header'],json=body,files=files)

			print(response.status_code,response.json())
			return response.json()
		except:
			print(url,mothod,body)

	def get_response_value(self,values,value):
		api_action=jsonpath.jsonpath(values,value)
		return api_action[0]

	def connect_mysql(self,mysql_host,mysql_db,username='root',port=13306,password='epochn'):
		conn = pymysql.connect(host=mysql_host,
							   user=username,
							   passwd=password,
							   db=mysql_db,
							   port=port,
							   charset='utf8mb4')
		self.set_conn_mysql(conn)
		cur = self.conn.cursor()
		self.set_cur_mysql(cur)

	def sqlalchemy_mysql(self,mysql_host,mysql_db,username='root',port=13306,password='epochn'):
		engine_url = f'mysql+pymysql://{username}:{password}@{mysql_host}:{port}/{mysql_db}'
		loonflow_engine = create_engine(engine_url)
		Session = sessionmaker(bind=loonflow_engine)
		self.db_session = Session()

	def set_cur_mysql(self,cur):
		self.cur=cur

	def set_conn_mysql(self,conn):
		self.conn=conn

	def query_mysql(self,sql,conditon='all'):
		self.cur.execute(sql)
		if conditon=='one':
			result=self.cur.fetchone()
		elif conditon=='all':
			result=self.cur.fetchall()
		else:
			result=self.conn.commit()
		return result

	def get_img(self,dict_keys):
		img_path = f"{os.path.dirname(os.path.abspath(__file__))}/123.jpg"
		files=[(dict_key, open(f'{img_path}', 'rb')) for dict_key in dict_keys]
		return files

	def read_excle(self,file_path='D:\自动化脚本\API',file_name='华世界常用接口文档.xlsx'):
		os.chdir(file_path)
		file = xlrd.open_workbook(file_name, 'r')
		tabs = file.sheet_names()
		api_information = []
		for tab in range(1, len(tabs)):
			get_tab = file.sheet_by_index(tab)
			rows = get_tab.nrows
			for i in range(1, rows):
				get_price = get_tab.row_values(i)
				values = [i] + get_price
				api_information.append(values)
		return api_information

	def read_excle_one_sheet(self,tab,file_path='D:\自动化脚本\API',file_name='华世界常用接口文档.xlsx'):
		os.chdir(file_path)
		file = xlrd.open_workbook(file_name, 'r')
		api_information = []
		get_tab = file.sheet_by_index(tab)
		rows = get_tab.nrows
		for i in range(1, rows):
			get_price = get_tab.row_values(i)
			values=[i]+get_price
			api_information.append(values)
		return api_information

	def write_excle(self,values,file_path='D:\自动化脚本\API\接口测试结果',file_name='测试结果.xlsx'):
		os.chdir(file_path)
		name = datetime.datetime.now().strftime("%Y%m%d-%H%M") + file_name
		file = xlwt.Workbook(name)
		sheet = file.add_sheet('测试结果')
		for i in range(len(values)):
			for j in range(len(values[i])):
				sheet.write(i, j, values[i][j])
		file.save(name)

if __name__ == '__main__':
	test=CommonMethod('11')
	mysql_host='192.168.188.12'
	mysql_db='epodb_20200902'
	for i in range(10455,10459):
		try:
			sql=f"UPDATE order_checkgoodsbill SET `update_time` = '2020-12-10 10:10:21' WHERE `order_id` = {i};"
			test.connect_mysql(mysql_host,mysql_db)
			test.query_mysql(sql,conditon='inster')
		except Exception as e:
			print(e)