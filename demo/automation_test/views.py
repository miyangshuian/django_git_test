from django.shortcuts import render,HttpResponse,redirect
from django.urls import reverse
from tabulate import tabulate
from automation_test.models import *

# Create your views here.

def baseinfo(port):
	hostinfo = BaseTestInformation.objects.filter(host_name=port).first()
	msg = f'{port}测试环境参数，如有更改请更新并提交；否则直接进入'
	if not hostinfo:
		hostinfo = BaseTestInformation.objects.filter(host_name='10157').first()
		msg = f'{port}测试环境不存在,使用10157默认测试环境参数，如有更改请更新并提交'
	host_name = hostinfo.host_name
	host_port = hostinfo.host_port
	host_mysql = hostinfo.host_mysql
	base_catelog = hostinfo.base_catelog
	base_catelog_id = hostinfo.base_catelog_id
	base_price = hostinfo.base_price
	sale_id_1 = hostinfo.sale_id_1
	sale_id_2 = hostinfo.sale_id_2
	values = []
	for i in ['施工方', '华立方', '渠道商', '华元素', '生产商-订单', '生产商-智能招标']:
		logininfo = BaseLoginInformation.objects.filter(user_type_name=i).first()
		user_name = logininfo.user_name
		user_password = logininfo.user_password
		user_type_name = logininfo.user_type_name
		user_type_id = logininfo.user_type_id
		user_company = logininfo.user_company
		user_company_id = logininfo.user_company_id
		values.append({'user_name': user_name, 'user_password': user_password, 'user_type_name': user_type_name,
					   'user_type_id': user_type_id, 'user_company': user_company, 'user_company_id': user_company_id})
	payrates = []
	for j in ['生产商与华元素', '华元素与华立方', '华立方与施工方', '华立方与渠道商', '渠道商与华元素']:
		payrate = BasePayRateInformation.objects.filter(payrate_type=j).first()
		scales = payrate.scales
		prepayPercent = payrate.prepayPercent
		deliveryPercent = payrate.deliveryPercent
		arrivalPercent = payrate.arrivalPercent
		installPercent = payrate.installPercent
		finishPercent = payrate.finishPercent
		warrantyPercent = payrate.warrantyPercent
		payrates.append(
			{'payrate_type': j, 'scales': scales, 'prepayPercent': prepayPercent, 'deliveryPercent': deliveryPercent,
			 'arrivalPercent': arrivalPercent, 'installPercent': installPercent, 'finishPercent': finishPercent,
			 'warrantyPercent': warrantyPercent})
	return msg,host_name,host_port,host_mysql,base_catelog,base_catelog_id,base_price,sale_id_1,sale_id_2,values,payrates

def index(request):
	return render(request,'index.html')

def index1(request):
	port=request.POST.get('port','')
	msg, host_name,host_port, host_mysql, base_catelog, base_catelog_id, base_price, sale_id_1, sale_id_2, values, payrates = baseinfo(port)
	msg=f'{port}测试环境基础数据如下：'
	return render(request, 'commoninfo.html', locals())

def showcurr(request,port):
	msg, host_name, host_port, host_mysql, base_catelog, base_catelog_id, base_price, sale_id_1, sale_id_2, values, payrates=baseinfo(port)
	a=tabulate([[msg]],tablefmt='html')
	b=tabulate([['测试端口:',host_name],['测试环境:',host_port], ['使用数据库:',host_mysql]],tablefmt='html')
	c=tabulate([['商品所属行业:',base_catelog], ['商品所属行业ID:',base_catelog_id], ['商品零售单价:',base_price], ['订单中商品ID:',sale_id_1, sale_id_2]],tablefmt='html')
	d=tabulate([[value] for value in values ],tablefmt='html')
	e=tabulate([[payrate] for payrate in payrates],tablefmt='html')
	f=f'<div><a href="/automation/api_test/epochn_process/{host_name}">选择执行脚本</a></div>'
	g='<div><a href="/automation/api_test/">重新设置基础信息</a></div>'
	return HttpResponse((a,b,c,d,e,f,g))

def updateinfo(request):
	values=request.POST
	host_name=values.get('host_name', '')
	obj=BaseTestInformation.objects.filter(host_name=host_name)
	if obj:
		obj.update(host_name=values.get('host_name',''),
				   host_port=values.get('host_port', ''),
				   host_mysql=values.get('host_mysql', ''),
				   sale_id_1=values.get('sale_id_1', ''),
				   sale_id_2=values.get('sale_id_2', ''),
				   base_catelog=values.get('base_catelog', ''),
				   base_catelog_id=values.get('base_catelog_id', ''),
				   base_price=values.get('base_price', ''),
				   )
	else:
		add_obj=BaseTestInformation(host_name=values.get('host_name',''),
									host_port=values.get('host_port', ''),
									host_mysql=values.get('host_mysql', ''),
									sale_id_1=values.get('sale_id_1', ''),
									sale_id_2=values.get('sale_id_2', ''),
									base_catelog=values.get('base_catelog', ''),
									base_catelog_id=values.get('base_catelog_id', ''),
									base_price=values.get('base_price', ''))
		add_obj.save()
	user_name=values.getlist('user_name','')
	user_password=values.getlist('user_password','')
	user_type_name=values.getlist('user_type_name','')
	user_type_id=values.getlist('user_type_id','')
	user_company=values.getlist('user_company','')
	user_company_id=values.getlist('user_company_id','')
	for i in range(len(user_type_name)):
		obj1=BaseLoginInformation.objects.filter(user_type_name=user_type_name[i])
		obj1.update(user_password=user_password[i],
					user_name=user_name[i],
					user_type_id=user_type_id[i],
					user_company=user_company[i],
					user_company_id=user_company_id[i])
	payrate_type=values.getlist('payrate_type','')
	scales=values.getlist('scales','')
	prepayPercent=values.getlist('prepayPercent','')
	deliveryPercent=values.getlist('deliveryPercent','')
	arrivalPercent=values.getlist('arrivalPercent','')
	installPercent=values.getlist('installPercent','')
	finishPercent=values.getlist('finishPercent','')
	warrantyPercent=values.getlist('warrantyPercent','')
	for j in range(len(payrate_type)):
		obj2=BasePayRateInformation.objects.filter(payrate_type=payrate_type[j])
		obj2.update(scales=scales[j],
					prepayPercent=prepayPercent[j],
					deliveryPercent=deliveryPercent[j],
					arrivalPercent=arrivalPercent[j],
					installPercent=installPercent[j],
					finishPercent=finishPercent[j],
					warrantyPercent=warrantyPercent[j])
	return redirect(reverse('automation_test:commoninfo_show',kwargs={'port': host_name}))


