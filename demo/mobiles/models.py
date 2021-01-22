from django.db import models

# Create your models here.
class User_test(models.Model):
	user_name=models.CharField('用户', max_length=200, null=True)
	user_password = models.CharField('密码', max_length=200)
	create_time = models.DateTimeField('创建时间', auto_now_add=True, null=True)
	record_status = models.CharField(verbose_name='状态', default='正常', max_length=20)
	from_type = models.CharField(verbose_name='来源', default='平台注册', max_length=20)