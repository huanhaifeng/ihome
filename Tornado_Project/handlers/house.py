# coding:utf-8

import json
import logging
import constans

from .BaseHandler import BaseHandler
from utils.response_code import RET
from utils.common import required_logined
from config import image_url_prefix


class AreaInfoHandler(BaseHandler):
	""""""
	def get(self):
		try:
			ret = self.redis.get("area_info")
		except Exception as e:
			logging.error(e)
			ret = None
		if ret:
			logging.debug(ret)
			logging.info("hit redis cache")
			return self.write('{"errno":%s, "errmsg":"OK", "data":%s}' % (RET.OK, ret))

		try:
			ret = self.db.query("select ai_area_id, ai_name from ih_area_info")
		except Exception as e:
			logging.error(e)
			return self.write(dict(errno=RET.DBERR, errmsg="get data error"))
		if not ret:
			return self.write(dict(errno=RET.NODATA, errmsg="no data error"))

		areas = []
		for l in ret:
			area = {
				"area_id": l["ai_area_id"],
				"name": l["ai_name"]
			}
			areas.append(area)
		try:
			self.redis.setex("area_info", constans.AREA_INFO_REDIS_EXPIRE_SECOND, json.dumps(areas))
		except Exception as e:
			logging.error(e)

		self.write(dict(errno=RET.OK, errmsg="OK", data=areas))


class MyHouseHandler(BaseHandler):
	""""""
	@required_logined
	def get(self):
		user_id = self.session.data["user_id"]
		try:
			ret = self.db.query("select a.hi_house_id,a.hi_title,a.hi_price,a.hi_ctime,b.ai_name,a.hi_index_image_url from ih_house_info a inner join ih_area_info b on a.hi_area_id=b.ai_area_id where a.hi_user_id=%s", user_id)
		except Exception as e:
			logging.error(e)
			return self.write(dict(errno=RET.DBERR, errmsg="get data error"))
		houses = []
		if ret:
			for l in ret:
				house = {
					"house_id": l["hi_house_id"],
					"title": l["hi_title"],
					"price": l["hi_price"],
					"ctime": l["hi_ctime"].strftime("%Y-%m-%d"),
					"area_name": l["ai_name"],
					"img_url": image_url_prefix + l["hi_index_image_url"] if l["hi_index_image_url"] else ""
				}
				houses.append(house)
		self.write(dict(errno=RET.OK, errmsg="OK", houses=houses))


class HouseInfoHandler(BaseHandler):
	""""""
	@required_logined
	def post(self):
		"""保存"""
		# 获取参数
        user_id = self.session.data.get("user_id")
        title = self.json_args.get("title")
        price = self.json_args.get("price")
        area_id = self.json_args.get("area_id")
        address = self.json_args.get("address")
        room_count = self.json_args.get("room_count")
        acreage = self.json_args.get("acreage")
        unit = self.json_args.get("unit")
        capacity = self.json_args.get("capacity")
        beds = self.json_args.get("beds")
        deposit = self.json_args.get("deposit")
        min_days = self.json_args.get("min_days")
        max_days = self.json_args.get("max_days")
        facility = self.json_args.get("facility") 
		# 校验
		if not all((title, price, area_id, address, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days)):
			return self.write(dict(errno=RET.PARAMERR, errmsg="缺少参数"))
		# 数据
		try:
			sql = "insert into ih_house_info(hi_user_id,hi_title,hi_price,hi_area_id,hi_address,hi_room_count, hi_acreage,hi_house_unit,hi_capacity,hi_beds,hi_deposit,hi_min_days,hi_max_days) values(%(user_id)s,%(title)s,%(price)s,%(area_id)s,%(address)s,%(room_count)s,%(acreage)s, %(house_unit)s,%(capacity)s,%(beds)s,%(deposit)s,%(min_days)s,%(max_days)s)"
			house_id = self.db.execute(sql, user_id=user_id, title=title, price=price, area_id=area_id, address=address, room_count=room_count,acreage=acreage, house_unit=unit, capacity=capacity, beds=beds,deposit=deposit, min_days=min_days, max_days=max_days)
		except Exception as e:
			logging.error(e)
			return self.write(dict(errno=RET.DBERR, errmsg="save data error"))

		try:
			# for fid in facility:
			# 	sql = "insert into ih_house_facility(hf_house_id, hf_facility_id) values(%s, %s)"
			# 	self.db.execute(sql, house_id, fid)
			sql = "insert into ih_house_facility(hf_house_id, hf_facility_id) values"
			sql_val = []
			vals = []
			for facility_id in facility:
				sql_val.append("%s, %s")
				vals.append(house_id)
				vals.append(facility_id)
			sql = ",".join(sql_val)
			vals = tuple(vals)
			self.db.execute(sql, *vals)
		except Exception as e:
			logging.error(e)
			try:
				self.db.execute("delete from ih_house_info where hi_house_id=%s", house_id)
			except Exception as e:
				logging.error(e)
				return self.write(dict(errno=RET.DBERR, errmsg="delete fail"))
			else:
				return self.write(dict(errno=RET.DBERR, errmsg="no data save"))
		# 返回
		self.write(dict(errno=RET.OK, errmsg="OK", house_id=house_id))