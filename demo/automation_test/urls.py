from django.conf.urls import url
from django.conf.urls import include
from automation_test import views

urlpatterns = [
    url(r'^$',views.index,name='automation_index'),
    url(r'^api_test/',include('automation_test.api_test.urls')),
    # url(r'^ui_test/',include('automation_test.ui_test.urls')),
    # url(r'^unit_api_test/',include('automation_test.unit_api_test.urls')),
]