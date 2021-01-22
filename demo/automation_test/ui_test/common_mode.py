from selenium import webdriver
import time,os
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from enum import Enum

class Constant(Enum):

	host = 'http://192.168.188.14:10157'
	sale_id = 1438024
	img_name = r'D:\资料\我的资料\模板\123.jpg'
	sgf_login_name = 'caoyuehua'
	hlf_login_name = '13418911156'
	qds_login_name = 'houdong'
	hys_login_name = 'duanye'
	scs_login_name = 'nuobeier'
	password='111111'
	common_string='123456'

class Common_method():

	def __init__(self,port):
		self.host=port
		self.driver=webdriver.Chrome()
		self.driver.maximize_window()
		self.action=ActionChains(self.driver)
		self.keys=Keys

	def get_url(self,url):
		return f'{self.host}{url}'

	def set_sgf_order(self,order):
		self.sgf_order=order

	def set_hlf_order(self,order):
		self.hlf_order=order

	def set_qds_order(self,order):
		self.qds_order=order

	def set_hys_order(self,order):
		self.hys_order=order

	def clear_pool(self):
		os.system("taskkill /f /im chromedriver.exe")
		os.system("taskkill /f /im chrome.exe")

	def select_element(self,path,type='xpath'):
		if type=='xpath':
			return self.driver.find_element_by_xpath(path)
		elif type=='id':
			return self.driver.find_element_by_id(path)
		elif type=='class':
			return self.driver.find_element_by_class_name(path)
		elif type=='tag':
			return self.driver.find_element_by_tag_name(path)
		elif type=='ccs':
			return self.driver.find_element_by_css_selector(path)
		elif type=='link':
			return self.driver.find_element_by_link_text(path)
		elif type=='xpaths':
			return self.driver.find_elements_by_xpath(path)
		elif type=='ids':
			return self.driver.find_elements_by_id(path)
		elif type=='classes':
			return self.driver.find_elements_by_class_name(path)
		elif type=='tags':
			return self.driver.find_elements_by_tag_name(path)
		elif type=='ccses':
			return self.driver.find_elements_by_css_selector(path)
		elif type=='links':
			return self.driver.find_elements_by_link_text(path)
		else:
			print('无效查找'.center(50,'='))

	def wait_type(self,type='hide',second=10,element=''):
		if type=='must':
			time.sleep(second)
		elif type=='hide':
			self.driver.implicitly_wait(second)
		elif type=='pres':
			locator = (By.XPATH, element)
			WebDriverWait(self.driver, second, 0.5).until(EC.presence_of_element_located(locator))
		else:
			print('请选择一种等待方式'.center(50,'='))

if __name__ == '__main__':
	host='http://192.168.188.14:10157'
	test=Common_method(host)
	constant=Constant
	print(constant.sgf_login_name.value)
	test.clear_pool()
