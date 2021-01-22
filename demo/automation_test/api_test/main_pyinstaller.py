from automation_api import process


def chioce():
	choice_type = eval(input('请选择执行脚本，\n1 注册新用户，授予权限；\n2 公司认证；\n3 批量上架商品-设置圈层价：战采；\n4 战采：订单流程；\n5 战采：订单全流程；\n6 智能招标'))
	modes=process
	if choice_type == 1:
		pass