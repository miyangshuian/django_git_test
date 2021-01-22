from django.db import models

# Create your models here.
class BaseLoginInformation(models.Model):
	user_name=models.CharField('用户名', max_length=200, null=True)
	user_password = models.CharField('密码',default='111111', max_length=200)
	user_type_name=models.CharField('用户类型', max_length=200, null=True)
	user_type_id=models.IntegerField('用户类型ID', null=True)
	user_company=models.CharField('用户所在公司', max_length=200, null=True)
	user_company_id=models.CharField('用户所在公司ID', max_length=200, null=True)

class BasePayRateInformation(models.Model):
	payrate_type=models.CharField('付款比例使用范围', max_length=200, null=True)
	scales=models.FloatField('折扣率',max_length=5)
	prepayPercent=models.FloatField('预付款比例',max_length=3)
	deliveryPercent=models.FloatField('发货款比例',max_length=3)
	arrivalPercent=models.FloatField('到货款比例',max_length=3)
	installPercent=models.FloatField('安装款比例',max_length=3)
	finishPercent=models.FloatField('结算款比例',max_length=3)
	warrantyPercent=models.FloatField('质保金比例',max_length=3)

class BaseTestInformation(models.Model):
	host_name=models.CharField('分支名称', max_length=50)
	host_port=models.CharField('测试环境', max_length=50)
	host_mysql=models.CharField('使用数据库', max_length=50)
	sale_id_1=models.IntegerField('订单中商品ID_1',default=0)
	sale_id_2=models.IntegerField('订单中商品ID_2',default=0)
	base_catelog_id=models.IntegerField('商品所属行业ID',default=622)
	base_catelog=models.CharField('商品所属行业',max_length=20,default='抛光砖')
	base_price=models.FloatField('商品零售单价',default=200.0)

class BaseState(models.Model):
	modulor=models.CharField('功能模块', max_length=50)
	stop_state=models.CharField('停止状态', max_length=50)