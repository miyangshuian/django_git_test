from django.conf.urls import url
from django.conf.urls import include
from mobiles.mobile_son_1 import son_view_1

urlpatterns = [
    url(r'^$',son_view_1.index),
    url(r'^phone_1/',son_view_1.phone_1),
    url(r'^phone_2/',son_view_1.phone_2),
    url(r'^phone_3/',son_view_1.phone_3),
]