from django.http import HttpResponse,JsonResponse
from django.shortcuts import render
from automation_test.api_test.user_view import TestApi

def hello_word(request):
	a={'code':0,'msg':'hello word','version':1}
	return JsonResponse(a)

def index(request):
	return render(request,'login_1.html',locals())
