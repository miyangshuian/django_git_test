import requests


class Common_information():

	def __init__(self, host):
		self.environment = host
		self.session = requests.Session()

	def send_request(self, method, url, headers, params={}, files={}, status="form-data"):
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

			return response
		except:
			print(url)

	def get_img(self, dict_keys):
		# 上传图片
		with open(r'123.jpg', 'rb') as f:
			img = f.read()
		file = {}
		for i in dict_keys:
			file[i] = ('123.jpg', img)
		return file
