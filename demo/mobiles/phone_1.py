from django.http import HttpResponse,JsonResponse

def index(request):
	return HttpResponse('mobiles 主页')

def phone_1(request):
	a={'code':0,'msg':'mobiles phone_1','version':1}
	return JsonResponse(a)

def phone_2(request):
	a={'code':0,'msg':'mobiles phone_2','version':1}
	return JsonResponse(a)

def phone_3(request):
	a={'code':0,'msg':'mobiles phone_3','version':1}
	return JsonResponse(a)