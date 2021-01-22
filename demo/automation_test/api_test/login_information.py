import requests

class Login_envirment():

	def __init__(self,host):
		self.environment=host
		self.session=requests.Session()

	def header_information(self,csrftoken):
		head = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36",
					 "Connection": "keep-alive",
					 "Cookie": csrftoken[0],
					 "Host": self.environment[7:],
					 "Accept" :"application/json",
					 "X-Requested-With": "XMLHttpRequest"}
		return head

	def user_login(self, user,csrftoken,header_information):
		url = self.environment + '/accounts/login'
		data = {'username': [str(user)], 'password': ['111111'], 'is_auto': ['false'],
				'csrfmiddlewaretoken': csrftoken[1]}
		res = self.session.post(url, data=data, headers=header_information)
		print(res.status_code,res.text)
		get_token = requests.utils.dict_from_cookiejar(res.cookies)
		# login_token='csrftoken={}; sessionid={}'.format(get_token['csrftoken'],get_token['sessionid'])
		login_token = 'csrftoken=%s; sessionid=%s '% (get_token['csrftoken'], get_token['sessionid'])
		header_information["Cookie" ] =login_token
		login_information={'header':header_information,'csrftoken':csrftoken[1]}
		return login_information

	def get_csrftoken(self):
		url = self.environment + '/accounts/login?next=/&query='
		res = self.session.get(url)
		result1 = res.headers
		result3 = result1.get('Set-Cookie')[0:74]
		result = res.text
		csrfmiddlewaretoken = result.split('var token = ')
		result2 = csrfmiddlewaretoken[1][1:65]
		return result3, result2

	def get_login_token(self,user):
		csrftoken=self.get_csrftoken()
		header_information=self.header_information(csrftoken)
		login_token=self.user_login(user,csrftoken,header_information)
		return login_token

if __name__ == '__main__':
	host = 'http://dev.echronos.com:10481'
	user = 'nuobeier'
	test = Login_envirment(host)
	test.get_login_token(user)

