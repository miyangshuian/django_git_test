from automation_test.unit_api_test.common_mode import Constant
from automation_test.unit_api_test.common_mode import CommonMethod
from automation_test.unit_api_test.login_information import Login_envirment
from automation_test.automation_api import All_api
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Float,Integer,Boolean,DateTime,Column,String
from jsonpath import jsonpath
import unittest
import warnings

host='http://192.168.188.14:10157'
mysql_host='192.168.188.12'
mysql_db='epodb_20201108'
Base_sqlalchemy=declarative_base()

class PayPercent(Base_sqlalchemy):
	__tablename__ = 'circle_price_circleprice'

	id = Column(Integer, primary_key=True, autoincrement=True)
	member = Column(String(32))
	company = Column(String(128))
	name = Column(String(128))
	shelf_life = Column(Float(2))
	depositPercent = Column(Float(2))
	prepayPercent = Column(Float(2))
	deliveryPercent = Column(Float(2))
	arrivalPercent = Column(Float(2))
	installPercent = Column(Float(2))
	finishPercent = Column(Float(2))
	warrantyPercent = Column(Float(2))
	system = Column(Boolean,default=False)
	isdefault = Column(Boolean,default=False)
	is_new_order = Column(Boolean,default=False)
	isDelete = Column(Boolean,default=False)
	prepayPercentDay = Column(Integer)
	deliveryPercentDay = Column(Integer)
	arrivalPercentDay = Column(Integer)
	installPercentDay = Column(Integer)
	finishPercentDay = Column(Integer)
	warrantyPercentDay = Column(Integer)
	create_time = Column(DateTime)
	update_time = Column(DateTime)

class BaseInformation():

	def __init__(self):
		self.commonmethod=CommonMethod(host)
		self.constant=Constant
		self.loginenvirment=Login_envirment(host)

	def set_cookies(self):
		self.shigongfang_cookies=self.loginenvirment.get_login_token(self.constant.common_sgf_sign.value,
																	 self.constant.common_sgf_company_type.value)
		self.hualifang_cookies = self.loginenvirment.get_login_token(self.constant.common_hlf_sign.value,
																	 self.constant.common_hlf_company_type.value)
		self.qudaoshang_cookies = self.loginenvirment.get_login_token(self.constant.common_qds_sign.value,
																	  self.constant.common_qds_company_type.value)
		self.huayuansu_cookies = self.loginenvirment.get_login_token(self.constant.common_hys_sign.value,
																	 self.constant.common_hys_company_type.value)
		self.changshang_cookies = self.loginenvirment.get_login_token(self.constant.common_scs_sign.value,
																	  self.constant.common_scs_company_type.value)
		return self.shigongfang_cookies,self.hualifang_cookies,self.qudaoshang_cookies,self.huayuansu_cookies,self.changshang_cookies,

class DepartMent(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		warnings.simplefilter("ignore", ResourceWarning)
		cls.allapi = All_api(host)
		user_login=BaseInformation().set_cookies()
		cls.sgf,cls.hlf,cls.qds,cls.hys,cls.scs=user_login
		cls.conn=CommonMethod(host)
		cls.conn.connect_mysql(mysql_host,mysql_db)
		cls.constant = Constant

	@classmethod
	def tearDownClass(cls):
		pass

	def test_1(self):
		company_id=self.constant.common_scs_company_id.value
		sql=f'select * from backend_department dep where dep.company_id="{company_id}"'
		hope=self.conn.query_mysql(sql)
		test_api=self.allapi.all_company_deparment(self.scs)
		department_id=jsonpath(test_api.json(),'$.data.department[0].id')[0]
		sql_1 = f'select * from backend_department dep where dep.id="{department_id}"'
		action=self.conn.query_mysql(sql_1,conditon='one')
		try:
			self.assertIn(action,hope)
		except Exception as e:
			print('='*10,e)

	def test_2(self):
		company_id = self.constant.common_scs_company_id.value
		departname=self.constant.common_information.value
		sql = f'select dep.id from backend_department dep where dep.company_id="{company_id}"'
		hope_1 = self.conn.query_mysql(sql)
		self.allapi.add_new_department(self.scs,departname)
		conn = CommonMethod(host)
		conn.connect_mysql(mysql_host, mysql_db)
		test_api = self.allapi.all_company_deparment(self.scs)
		department_id=list(filter(lambda x:x['name']==departname,test_api.json()['data']['department']))[0]['id']
		action=(department_id,)
		sql_2 = f'select dep.id from backend_department dep where dep.company_id="{company_id}"'
		hope_2 = conn.query_mysql(sql_2)
		try:
			self.assertIn(action, hope_2)
			self.assertNotIn(action, hope_1)
		except Exception as e:
			print('='*10,e)

class ManegeTemplate(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		warnings.simplefilter("ignore", ResourceWarning)
		cls.allapi = All_api(host)
		user_login = BaseInformation().set_cookies()
		cls.sgf, cls.hlf, cls.qds, cls.hys, cls.scs = user_login
		cls.conn = CommonMethod(host)
		cls.conn.connect_mysql(mysql_host, mysql_db)
		cls.constant = Constant

	@classmethod
	def tearDownClass(cls):
		pass

	def test_1(self):
		payrate_list=self.constant.common_payrate_list.value
		action=float(payrate_list[0])
		payrate_id=self.allapi.get_payrate(self.scs,payrate_list)
		sql=f"SELECT prepayPercent FROM backend_paypercent WHERE id = '{payrate_id}' "
		hope=self.conn.query_mysql(sql,conditon='one')
		try:
			self.assertEqual(action,hope[0])
		except Exception as e:
			print('='*10,e)

	def test_2(self):
		payrate_list = self.constant.common_payrate_list.value
		payrate_id = self.allapi.get_payrate(self.scs, payrate_list)
		sql = f"SELECT isDelete FROM backend_paypercent WHERE id = '{payrate_id}' "
		hope = self.conn.query_mysql(sql, conditon='one')[0]
		self.allapi.delete_payrate(self.scs,payrate_id)
		conn = CommonMethod(host)
		conn.connect_mysql(mysql_host, mysql_db)
		hope_1=conn.query_mysql(sql,conditon='one')[0]
		try:
			self.assertEqual(hope, 0)
			self.assertEqual(hope_1, 1)
		except Exception as e:
			print('=' * 10, e)

class CirclePrice(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		warnings.simplefilter("ignore", ResourceWarning)
		cls.allapi = All_api(host)
		user_login = BaseInformation().set_cookies()
		cls.sgf, cls.hlf, cls.qds, cls.hys, cls.scs = user_login
		cls.conn = CommonMethod(host)
		cls.conn.sqlalchemy_mysql(mysql_host, mysql_db)
		cls.constant = Constant

	@classmethod
	def tearDownClass(cls):
		pass

	def test_1(self):
		res=self.allapi.get_circle_list(self.scs)
		circle_id=res.json()['data'][0]['id']
		values=self.conn.db_session.query(PayPercent).filter(PayPercent.id==circle_id).first()
		print(values.id)

if __name__ == '__main__':
	suite1 = unittest.TestLoader().loadTestsFromTestCase(DepartMent)
	suite2 = unittest.TestLoader().loadTestsFromTestCase(ManegeTemplate)
	suite3 = unittest.TestLoader().loadTestsFromTestCase(CirclePrice)
	suite = unittest.TestSuite([suite1,suite2])
	unittest.TextTestRunner(verbosity=2).run(suite)
