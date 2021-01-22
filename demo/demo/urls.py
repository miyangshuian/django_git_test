"""demo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.conf.urls import include
from django.contrib import admin
from demo import view_one
from mobiles.views import MobileClass,Register
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    url(r'^$', view_one.index),
    url(r'^test/', view_one.hello_word),
    url(r'^phones/',include('mobiles.urls')),
    url(r'^login_in/$',csrf_exempt(MobileClass.as_view())),
    url(r'^register/$',csrf_exempt(Register.as_view())),
    url(r'^automation/', include('automation_test.urls',namespace='automation_test')),
]
