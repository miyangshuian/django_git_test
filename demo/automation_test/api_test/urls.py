from django.conf.urls import url
from automation_test.api_test.user_view import EpochnProcess
from automation_test import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    url(r'^$',views.index1),
    url(r'^update/commoninfo/',views.updateinfo),
    url(r'^show/(?P<port>\d+)$',views.showcurr,name='commoninfo_show'),
    url(r'^epochn_process/(?P<port>\d+)$',csrf_exempt(EpochnProcess.as_view()),name='epochn_process'),
	]