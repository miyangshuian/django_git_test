from django.conf.urls import url
from django.conf.urls import include
from mobiles import phone_1

urlpatterns = [
    url(r'^$',phone_1.index),
    url(r'^phone_1/',phone_1.phone_1),
    url(r'^phone_2/',phone_1.phone_2),
    url(r'^phone_3/',phone_1.phone_3),
    url(r'^phone_son/',include('mobiles.mobile_son_1.urls')),
]
