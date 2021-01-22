from enum import Enum

class OrderState(Enum):
	sgf_submit_order='施工方提交订单'
	hlf_split_order='华立方分单'
	qds_review_order='渠道商接单'
	scs_compare_order='生产商备货完成'
	sgf_accept_order='施工方到货验收'
	hlf_accept_order='华立方到货验收'
	hys_accept_order='华元素到货验收'
	sgf_split_batches='施工方分批完成'