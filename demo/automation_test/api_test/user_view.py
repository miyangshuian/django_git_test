from django.shortcuts import render
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect
from django.views.generic.base import View
from automation_test.models import *
from automation_test.api_test.process import Use_modle
from automation_test.models import *
import random

class TestApi(View):

	def get_common_info(self,name):
		baseinfo=BaseTestInformation.objects.filter(host_name=name).first()
		return baseinfo

	def get_login_info(self,name='施工方'):
		baseinfo=BaseLoginInformation.objects.filter(user_type_name=name).first()
		return baseinfo

	def get_payrate_list(self,name='默认付款比例'):
		baseinfo=BasePayRateInformation.objects.filter(payrate_type=name).first()
		return baseinfo

	def get(self,request):
		hostinfo = self.get_common_info()
		host_port = hostinfo.host_port
		host_mysql = hostinfo.host_mysql
		base_catelog = hostinfo.base_catelog
		base_catelog_id = hostinfo.base_catelog_id
		base_price = hostinfo.base_price
		sale_id_1 = hostinfo.sale_id_1
		sale_id_2 = hostinfo.sale_id_2
		values = []
		for i in ['施工方', '华立方', '渠道商', '华元素', '生产商-订单', '生产商-智能招标']:
			logininfo = tt.get_login_info(i)
			user_name = logininfo.user_name
			user_password = logininfo.user_password
			user_type_name = logininfo.user_type_name
			user_type_id = logininfo.user_type_id
			user_company = logininfo.user_company
			user_company_id = logininfo.user_company_id
			values.append({'user_name': user_name, 'user_password': user_password, 'user_type_name': user_type_name,
						   'user_type_id': user_type_id, 'user_company': user_company,
						   'user_company_id': user_company_id})
		payrates = []
		for j in ['生产商与华元素', '华元素与华立方', '华立方与施工方', '华立方与渠道商', '渠道商与华元素']:
			payrate = tt.get_payrate_list(j)
			scales = payrate.scales
			prepayPercent = payrate.prepayPercent
			deliveryPercent = payrate.deliveryPercent
			arrivalPercent = payrate.arrivalPercent
			installPercent = payrate.installPercent
			finishPercent = payrate.finishPercent
			warrantyPercent = payrate.warrantyPercent
			payrates.append({'payrate_type': j, 'scales': scales, 'prepayPercent': prepayPercent,
							 'deliveryPercent': deliveryPercent,
							 'arrivalPercent': arrivalPercent, 'installPercent': installPercent,
							 'finishPercent': finishPercent, 'warrantyPercent': warrantyPercent})
		msg = 'success'
		return render(request, 'commoninfo.html', locals())

class EpochnProcess(View):

	def get(self,request,port):
		port_name=BaseTestInformation.objects.filter(host_name=port).first()
		host_name=port_name.host_name
		values_order=BaseState.objects.filter(modulor='订单流程')
		values_binding=BaseState.objects.filter(modulor__in=['智能招标','圈层价','注册账户','公司认证'])
		values2={'order':[i.stop_state for i in values_order],'bingding':[i.stop_state for i in values_binding]}
		return render(request,'choice_process.html',locals())

	def post(self,request,port):
		self.basetestinfo(port)
		modular=request.POST.get('value1','')
		stop_state=request.POST.get('value2','所有流程')
		conditions=request.POST.get('value3','')
		condition=1 if conditions=='分批' else 0
		mode = Use_modle(self.host_name)
		mode.set_cookies(self.users_information)
		if modular=='订单流程':
			mode.all_order_process(self.sale_id,self.payrate_ids,condition=condition,is_stop=stop_state)
			return JsonResponse({'code': 0, 'msg': 'order process compare', 'version': 1})
		elif modular=='智能招标':
			mode.start_bidding(is_stop=stop_state)
			return JsonResponse({'code': 0, 'msg': 'bidding process compare', 'version': 1})
		elif modular=='圈层价':
			sale_ids=mode.upload_goods_to_circle(self.scales, self.users_information,self.payrate_ids,catelog_id=self.catelog_id,price=self.price,is_stop=stop_state)
			return JsonResponse({'code': 0, 'msg': 'upload_goods_to_circle compare','sale_ids':sale_ids, 'version': 1})
		elif modular=='注册账户':
			phone=mode.add_personal_give_roles(self.users_information)
			return JsonResponse({'code': 0, 'msg': 'add_personal_give_roles compare','phone':phone, 'version': 1})
		elif modular=='公司认证':
			company_name=random.choice(self.names_company)
			company=mode.prove_company(names=company_name)
			return JsonResponse({'code': 0, 'msg': 'prove_company compare','company_info':company, 'version': 1})
		return JsonResponse({'code':-1,'msg':'请重新执行脚本','version':1})

	def basetestinfo(self,port):
		hostinfo=BaseTestInformation.objects.filter(host_name=port).first()
		self.host_name = hostinfo.host_port
		self.host_mysql=hostinfo.host_mysql
		self.catelog_id = hostinfo.base_catelog_id
		self.price = hostinfo.base_price
		self.sale_id = {'product_id_1': hostinfo.sale_id_1, 'product_id_2': hostinfo.sale_id_2}
		self.names_company = ['汽车服务','金融服务','科技创新','五金材料','基建材料','装修材料']
		logininfo_sgf = BaseLoginInformation.objects.filter(user_type_name='施工方').first()
		logininfo_hlf = BaseLoginInformation.objects.filter(user_type_name='华立方').first()
		logininfo_qds = BaseLoginInformation.objects.filter(user_type_name='渠道商').first()
		logininfo_hys = BaseLoginInformation.objects.filter(user_type_name='华元素').first()
		logininfo_scs_dd = BaseLoginInformation.objects.filter(user_type_name='生产商-订单').first()
		logininfo_scs_zb = BaseLoginInformation.objects.filter(user_type_name='生产商-智能招标').first()
		self.users_information = {
			'shigongfang': {'fuzheren': logininfo_sgf.user_name, 'account_type': logininfo_sgf.user_type_id, 'company_name': logininfo_sgf.user_company,
							'company_id': logininfo_sgf.user_company_id,'password':logininfo_sgf.user_password},
			'hualifang': {'fuzheren': logininfo_hlf.user_name, 'account_type': logininfo_hlf.user_type_id, 'company_name': logininfo_hlf.user_company,
							'company_id': logininfo_hlf.user_company_id,'password':logininfo_hlf.user_password},
			'qudaoshang': {'fuzheren': logininfo_qds.user_name, 'account_type': logininfo_qds.user_type_id, 'company_name': logininfo_qds.user_company,
							'company_id': logininfo_qds.user_company_id,'password':logininfo_qds.user_password},
			'huayuansu': {'fuzheren': logininfo_hys.user_name, 'account_type': logininfo_hys.user_type_id, 'company_name': logininfo_hys.user_company,
							'company_id': logininfo_hys.user_company_id,'password':logininfo_hys.user_password},
			'changshang': {'fuzheren': logininfo_scs_dd.user_name, 'account_type': logininfo_scs_dd.user_type_id, 'company_name': logininfo_scs_dd.user_company,
							'company_id': logininfo_scs_dd.user_company_id,'password':logininfo_scs_dd.user_password},
			'changshang_zb': {'fuzheren': logininfo_scs_zb.user_name, 'account_type': logininfo_scs_zb.user_type_id,'company_name': logininfo_scs_zb.user_company,
						   'company_id': logininfo_scs_zb.user_company_id, 'password': logininfo_scs_zb.user_password}}
		payrate_cth = BasePayRateInformation.objects.filter(payrate_type='生产商与华元素').first()
		payrate_hth = BasePayRateInformation.objects.filter(payrate_type='华元素与华立方').first()
		payrate_hts = BasePayRateInformation.objects.filter(payrate_type='华立方与施工方').first()
		payrate_ftq = BasePayRateInformation.objects.filter(payrate_type='华立方与渠道商').first()
		payrate_qty = BasePayRateInformation.objects.filter(payrate_type='渠道商与华元素').first()
		self.payrate_ids = {'changshang_to_huayuansu': [payrate_cth.prepayPercent,payrate_cth.deliveryPercent,payrate_cth.arrivalPercent,
												   payrate_cth.installPercent,payrate_cth.finishPercent,payrate_cth.warrantyPercent],
					   'huayuansu_to_hualifang': [payrate_hth.prepayPercent,payrate_hth.deliveryPercent,payrate_hth.arrivalPercent,
												  payrate_hth.installPercent,payrate_hth.finishPercent,payrate_hth.warrantyPercent],
					   'hualifang_to_shigongfang': [payrate_hts.prepayPercent,payrate_hts.deliveryPercent,payrate_hts.arrivalPercent,
													payrate_hts.installPercent,payrate_hts.finishPercent,payrate_hts.warrantyPercent],
					   'hualifang_to_qudaoshang': [payrate_ftq.prepayPercent,payrate_ftq.deliveryPercent,payrate_ftq.arrivalPercent,
												   payrate_ftq.installPercent,payrate_ftq.finishPercent,payrate_ftq.warrantyPercent],
					   'huayuansu_to_qudaoshang': [payrate_qty.prepayPercent,payrate_qty.deliveryPercent,payrate_qty.arrivalPercent,
												   payrate_qty.installPercent,payrate_qty.finishPercent,payrate_qty.warrantyPercent]
					   }
		self.scales = {'changshang_to_huayuansu': payrate_cth.scales,
				  'huayuansu_to_hualifang': payrate_hth.scales,
				  'huayuansu_to_qudaoshang': payrate_qty.scales,
				  'hualifang_to_shigongfang': payrate_hts.scales,
				  'hualifang_to_qudaoshang': payrate_ftq.scales,}