# -*- coding: utf-8 -*-
#idprod:id_prod, userid:user_id, bid:user_bid
import json
class Bid(object):
	def __init__(self, j):
		self.__dict__ = json.loads(j)