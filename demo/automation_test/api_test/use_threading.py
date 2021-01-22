import threading
from multiprocessing import Pool
from automation_api.process import Use_modle

# class MyThreading(threading.Thread):
#
# 	def __init__(self, func, arg):
# 		super(MyThreading,self).__init__()
# 		self.func = func
# 		self.arg = arg
# 		print(func,arg)
#
# 	def run(self):
# 		self.func(self.arg)
#
# def my_func(args):
# 	"""
# 	你可以把任何你想让线程做的事定义在这里
# 	"""
# 	Use_modle.pay_cash(args)

if __name__ == '__main__':
	host = 'http://192.168.188.14:10157'
	users_information = {
		'shigongfang': {'fuzheren': 'caoyuehua', 'account_type': 5, 'company_name': '河南平安实业有限公司', 'company_id': 174},
		'hualifang': {'fuzheren': 'zhangzihanghlf', 'caiwu': 'wangjialehys1', 'dingdan': 'chengzhefeng',
					  'shenpi': 'monica',
					  'account_type': 1, 'company_name': '深圳市华立方商业集团有限公司', 'company_id': 33},
		'qudaoshang': {'fuzheren': 'houdong', 'account_type': 4, 'company_name': '河南浩海商贸有限公司', 'company_id': 153},
		'huayuansu': {'fuzheren': 'chenshanshan', 'caiwu': 'wangjialehys1', 'dingdan': 'wangjialehys1', 'shenpi': 'monica',
					  'account_type': 2, 'company_name': '华元素采购（深圳）有限公司', 'company_id': 34},
		'changshang': {'fuzheren': 'nuobeier', 'other': 'SKS123', 'account_type': 3, 'company_name': '杭州诺贝尔陶瓷有限公司',
					   'company_id': 86}
	}
	payrate_ids = {'changshang_to_huayuansu': [100, 0, 0, 0, 0, 0],
				   'huayuansu_to_hualifang': [100, 0, 0, 0, 0, 0],
				   'hualifang_to_shigongfang': [100, 0, 0, 0, 0, 0],
				   'hualifang_to_qudaoshang': [100, 0, 0, 0, 0, 0],
				   'huayuansu_to_qudaoshang': [100, 0, 0, 0, 0, 0]}
	scales = {'changshang_to_huayuansu': 80,
			  'huayuansu_to_hualifang': 85,
			  'huayuansu_to_qudaoshang': 85,
			  'hualifang_to_shigongfang': 90}
	names_company = '汽车服务'
	process = Use_modle(host)
	process.set_cookies(users_information)
	p=Pool()
	for i in range(10):
		p.apply_async(process.start_bidding)
	p.close()
	p.join()
# 	sale_id = {'product_id_1': 1171755, 'product_id_2': 1171756}
# 	lock=threading.Lock()
# 	re_lock=threading.RLock()
#
# 	for i in range(2):
# 	# 	obj = threading.Thread(target=process.pay_cash,args=(users_information,))
# 	# 	obj = threading.Thread(target=process.only_order_process,args=(sale_id,payrate_ids,0,lock))
# 		obj = threading.Thread(target=process.all_order_process,args=(sale_id,payrate_ids,0,lock))
# 		re_lock.acquire()
# 		obj = threading.Thread(target=process.start_bidding,args=(lock,))
# 		re_lock.release()
# 		obj.start()
#
# # number = 0
# def plus(lk,a):
#
# 	# lock = threading.Lock()
# 	global number #	 global声明此处的number是外面的全局变量number
# 	lk.acquire()		# 开始加锁
# 	print(a)
# 	for _ in range(1000000):	# 进行一个大数级别的循环加一运算
# 		number += 1
# 	print("子线程%s运算结束后，number = %s" % (threading.current_thread().getName(), number))
# 	lk.release()		# 释放锁，让别的线程也可以访问number
#
# if __name__ == '__main__':
# 	for i in range(2):		# 用2个子线程，就可以观察到脏数据
# 		t = threading.Thread(target=plus, args=(lock,111)) # 需要把锁当做参数传递给plus函数
# 		t.start()
# 	time.sleep(2)		# 等待2秒，确保2个子线程都已经结束运算。
# 	print("主线程执行完毕后，number = ", number)