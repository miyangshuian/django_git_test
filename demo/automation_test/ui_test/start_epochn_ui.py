from automation_test.ui_test.common_mode import Common_method
from automation_test.ui_test.common_mode import Constant


class Start_process(Common_method):

	def login_in(self,login_name,password):
		login_url='/accounts/login'
		url = self.get_url(login_url)
		login_name_element='//input[@type="text"]'
		login_password_element='//input[@type="password"]'
		login_submit_element='//button[@type="submit"]'
		wait_element='//div[@title="管生意"]'
		self.driver.get(url)
		self.select_element(login_name_element).send_keys(login_name)
		self.select_element(login_password_element).send_keys(password)
		self.select_element(login_submit_element).click()
		self.wait_type(type='pres',element=wait_element)

	def add_sale(self,sale_id,shop_index='诺贝尔华世界店'):
		sale_url=f'/bk/sale/detail/{sale_id}/'
		url=self.get_url(sale_url)
		add_shop='//div[@class="product-operate"]'
		shop_sale='//i[@class="ech-icon-cart lt-navbar-item-icon"]'
		shop_namess='//span[@class="shop-name"]'
		submit_ele='//div[@class="text-right el-col el-col-14"]/button'
		eng_name='//div[@class="engineering-name"]/div/input'
		cin_unit='//div[@class="construction-unit"]/div/input'
		fapiao='//span[@class="el-radio__input"]'
		submit_order='//div[@class="ech-button-group__content is-fixed"]/button[2]'
		self.driver.get(url)
		self.wait_type(type='pres',element=add_shop)
		aa=self.select_element(add_shop)
		aa.find_element_by_xpath('//button[1]').click()
		self.wait_type()
		self.select_element(shop_sale).click()
		self.wait_type()
		shop_names=self.select_element(shop_namess,type='xpaths')
		shop=[]
		for i,shop_name in enumerate(shop_names):
			if shop_name.text==shop_index:
				shop.append(i+1)
		if not len(shop):
			self.driver.refresh()
			shop_names = self.select_element(shop_namess, type='xpaths')
			for i, shop_name in enumerate(shop_names):
				if shop_name.text == shop_index:
					shop.append(i + 1)
		sale_ele=f'//div[@class="el-scrollbar__view"]/div[position()={shop[0]}]/div[@class="cart-item-header"]/label'
		self.select_element(sale_ele).click()
		self.select_element(submit_ele).click()
		self.wait_type(type='pres',element=eng_name)
		self.select_element(eng_name).send_keys(constant.common_string.value)
		self.select_element(cin_unit).send_keys(constant.common_string.value)
		self.select_element(fapiao).click()
		self.select_element(submit_order).click()
		self.wait_type(type='must')

	def pay_order(self,condion=None):
		buy_order = '//div[@class="mar-b-10"]/span'
		pay_ele = '//div[@class="pt-2 text-right"]/span[2]/button[1]'
		pay_no='//div[@class="pay-no el-input"]/input'
		file_path='//div[@class="update-box flex-box"]/input'
		submit_pay='//div[@class="ech-button-group__content"]/button'
		if condion:
			self.select_element(buy_order).click()
			self.wait_type(type='must')
		self.wait_type(type='pres',element=pay_ele)
		order_code = self.driver.current_url
		print(order_code)
		self.select_element(pay_ele).click()
		self.wait_type()
		self.select_element(pay_no).send_keys(constant.common_string.value)
		self.select_element(file_path).send_keys(constant.img_name.value)
		self.select_element(submit_pay).click()
		self.wait_type()
		return order_code

	def shoukuan_order(self,url):
		get_pay_ele='//div[@class="pt-2 text-right"]/span/button[1]'
		money_num='//div[@class="collection-cell-box"]/div[6]/span[2]'
		money_ele='//div[@class="collection-cell-box"]/div[7]/div/input'
		subnit_pay='//div[@class="dialog-footer"]/button[2]'
		self.driver.get(url)
		self.wait_type(type='pres',element=get_pay_ele)
		self.select_element(get_pay_ele).click()
		self.wait_type(type='pres',element=money_num)
		moneys=self.select_element(money_num).text
		self.select_element(money_ele).send_keys(moneys[1:])
		self.select_element(subnit_pay).click()
		self.wait_type(type='must')

	def easy_split_order(self):
		split_order = '//div[@class="pt-2 text-right"]/span[3]/button'
		submit_order = '//div[@class="button-wrapper"]'
		self.wait_type(type='pres',element=split_order)
		self.select_element(split_order).click()
		self.wait_type(type='must')
		aa=self.select_element(submit_order)
		aa.find_element_by_xpath('//button[@class="el-button el-button--primary is-round"]/span').click()
		self.wait_type()

if __name__ == '__main__':
	constant = Constant
	test = Start_process(constant.host.value)
	test.login_in(constant.sgf_login_name.value,constant.password.value)
	test.add_sale(constant.sale_id.value)
	sgf_order_url=test.pay_order()
	# sgf_order_url='http://192.168.188.14:10157/orderinfo/themeapp/order/details/?pk=10703&order_type=new&type=buyOrder'
	test.login_in(constant.hlf_login_name.value,constant.password.value)
	test.shoukuan_order(sgf_order_url)
	test.easy_split_order()
	test.pay_order(constant.common_string.value)
