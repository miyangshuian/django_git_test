from django.http import HttpResponse,JsonResponse

def index(request):
	return HttpResponse('son 主页')

def phone_1(request):
	a={'code':0,'msg':'son phone_1','version':1}
	return JsonResponse(a)

def phone_2(request):
	a={'code':0,'msg':'son phone_2','version':1}
	return JsonResponse(a)

def phone_3(request):
	a={'code':0,'msg':'son phone_3','version':1}
	return JsonResponse(a)