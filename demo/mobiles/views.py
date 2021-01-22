from django.shortcuts import render,redirect
from django.urls import reverse
from django.http import HttpResponse,JsonResponse
from django.views.generic.base import View
from mobiles.models import *

class MobileClass(View):

	def get(self,request):
		user=request.GET.get('user','')
		if user=='admin':
			return redirect(reverse('automation_test:automation_index'))
		else:
			msg='请登录'
			return render(request,'login_1.html',locals())

	def post(self,request):
		user = request.POST.get("user", "")
		pwd = request.POST.get("pwd", "")
		msg=User_test.objects.filter(user_name=user,user_password=pwd).first()
		if msg:
			return redirect(reverse('automation_test:order_process'))
		else:
			msg='用户、密码不正确，请重新登录'
			return render(request,'login_1.html',locals())

class Register(View):

	def get(self,request):
		return render(request,'register.html')

	def post(self,request):
		user = request.POST.get("user", "")
		pwd1 = request.POST.get("pwd1", "")
		pwd2 = request.POST.get("pwd2", "")
		if pwd1==pwd2:
			obj=User_test(user_name=user,user_password=pwd1)
			try:
				obj.save()
				return JsonResponse({'code':0,'msg':'save success','version':1})
			except:
				return JsonResponse({'code': -1, 'msg': 'save fail', 'version': 1})
		else:
			return JsonResponse({'code':-1,'msg':'密码不正确','version':1})