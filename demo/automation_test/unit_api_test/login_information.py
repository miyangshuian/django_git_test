import requests

class Login_envirment():

	def __init__(self,environment):
		self.environment=environment
		self.session=requests.Session()

	def header_information(self):
		self.head = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36",
					 "Connection": "keep-alive",
					 "Cookie": self.header_csrftoken,
					 "Host": self.environment[7:],
					 "X-Requested-With": "XMLHttpRequest"}

	def user_login(self,user):
		url = self.environment+f'/accounts/login'
		data = {'username': [user], 'password': ['111111'], 'is_auto': ['false'],'csrfmiddlewaretoken': self.body_csrftoken}
		res = self.session.post(url,headers=self.head,data=data)
		get_token = requests.utils.dict_from_cookiejar(res.cookies)
		login_token = 'csrftoken=%s; sessionid=%s '% (get_token['csrftoken'], get_token['sessionid'])
		self.head["Cookie" ] =login_token
		self.head["Accept" ] ='application/json'
		login_information={'header':self.head,'csrftoken':self.body_csrftoken}
		return login_information

	def get_csrftoken(self):
		url = self.environment+f'/accounts/login?next=/&query='
		res = self.session.get(url)
		result1 = res.headers
		result3 = result1.get('Set-Cookie')[0:74]
		self.set_header_csrftoken(result3)
		result = res.text
		csrfmiddlewaretoken = result.split('var token = ')
		result2 = csrfmiddlewaretoken[1][1:65]
		self.set_body_csrftoken(result2)

	def set_header_csrftoken(self,csrftoken):
		self.header_csrftoken=csrftoken

	def set_body_csrftoken(self,csrftoken):
		self.body_csrftoken=csrftoken

	def get_companys_id(self,type):
		url = self.environment+f'/channel/business/get_self_companys/'
		res = self.session.get(url,headers=self.head)
		result = res.json()['data']
		res = list(filter(lambda x: type == x['account_type'] and x['name'] != '个人账户', result))[0]
		return {'company_id': res['id'], 'company_name': res['name']}

	def swith_to_company(self,company_information):
		url = self.environment+f'/channel/business/switch_company/'
		body = {'com_id':company_information.get('company_id', '')}
		res = self.session.post(url,headers=self.head,data=body)

	def get_login_token(self,user,type):
		self.get_csrftoken()
		self.header_information()
		login_token=self.user_login(user)
		company_infoemation=self.get_companys_id(type)
		self.swith_to_company(company_infoemation)
		return login_token

if __name__ == '__main__':
	host = 'http://192.168.178.130:8080'
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
	test=Login_envirment(host)
	for user in users_information:
		a=test.get_login_token(users_information[user]['fuzheren'],users_information[user]['account_type'])
		print(a)