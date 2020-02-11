# coding:utf-8

import json
import logging
import constans
import math

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


class HouseListHandler(BaseHandler):
	""""""
	def get(self):
		"""
	 名称			类型			是否必须	 	说明
	 start_date		string		否			
	 end_date		string		否
	 area_id		string		否
	 sort_key		string		否			默认时间倒序 new hot pri-inc pri-des
	 page			int			否			默认第一页
		"""
		# 获取参数
		start_date = self.get_argument("sd", "")
		end_date = self.get_argument("ed", "")
		area_id = self.get_argument("aid", "")
		sort_key = self.get_argument("sk", "new")
		page = self.get_argument("p", 1)

		# 参数校验
		try:
			ret = self.redis.hget("hl_%s_%s_%s_%s" % (start_date, end_date, area_id, sort_key), page)
		except Exception as e:
			logging.error(e)
			ret = None
		if ret:
			logging.info("hit redis")
			return self.write(ret)

		page = int(page)
		# 查询数据，涉及到的数据库表 ih_house_info ih_user_profile ih_order_info
		sql = "select distinct hi_house_id, hi_title, hi_price, hi_room_count, hi_index_image_url, hi_address, up_avatar, hi_ctime, hi_order_count from ih_house_info left join ih_order_info on hi_house_id=oi_house_id inner join ih_user_profile on hi_user_id=up_user_id"

		sql_where = []
		sql_params = {}
		if start_date and end_date:
			sql_where.append("(oi_begin_date is null and oi_end_date is null) or (not (oi_begin_date<=%(end_date)s and oi_end_date>=%(start_date)s))")
			sql_params["start_date"] = start_date
			sql_params["end_date"] = end_date
		elif start_date:
			sql_where.append("(oi_begin_date is null and oi_end_date is null) or (oi_end_date < %(start_date)s)")
			sql_params["start_date"] = start_date
		elif end_date:
			sql_where.append("(oi_begin_date is null and oi_end_date is null) or (oi_begin_date > %(end_date)s)")
			sql_params["end_date"] = end_date

		if area_id:
			sql_where.append("hi_area_id = %(area_id)s")
			sql_params["area_id"] = area_id

		sql = "select count(distinct hi_house_id) from ih_house_info left join ih_order_info on hi_house_id=oi_house_id"
		if sql_where:
			sql += "where"
			sql += "and".join(sql_where)
		try:
			ret = self.db.get(sql, **sql_params)
		except Exception as e:
			logging.error(e)
			total_page = -1
		else:
			total_page = int(math.ceil(ret["counts"]/float(constans.HOUSE_LIST_PAGE_CAPACITY)))
			if page>total_page:
				return self.write(dict(errno=RET.OK, errmsg="OK", total_page=total_page, data=[]))

		if sql_where:
			sql += "where"
			sql += "and".join(sql_where)

		if "new" == sort_key:
			sql += "order by hi_ctime desc"
		elif "hot" == sort_key:
			sql += "order by hi_order_count desc"
		elif "pri-inc" == sort_key:
			sql += "order by hi_price asc"
		elif "pri-des" == sort_key:
			sql = "order by hi_price desc"

		if 1 == page:
			sql += "limit %s" % (constans.HOUSE_LIST_PAGE_CAPACITY * constans.HOUSE_LIST_REIDS_CACHED_PAGE)
		else:
			sql += "limit %s,%s" % ((page-1)*constans.HOUSE_LIST_PAGE_CAPACITY, constans.HOUSE_LIST_PAGE_CAPACITY * constans.HOUSE_LIST_REIDS_CACHED_PAGE)

		logging.debug(sql)
		try:
			ret = self.db.query(sql, **sql_params)
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
					"room_count": l["hi_room_count"],
					"order_count": l["hi_order_count"],
					"address": l["hi_address"],
					"img_url": image_url_prefix + l["hi_index_image_url"] if l["hi_index_image_url"] else "",
					"avatar_url": image_url_prefix + l["up_avatar"] if l["up_avatar"] else ""
				}
				houses.append(house)

		cur_page_data = houses[:constans.HOUSE_LIST_PAGE_CAPACITY]
		redis_data = {}
		redis_data[str(page)] = json.dumps(dict(errno=RET.OK, errmsg="OK", data=cur_page_data, total_page=total_page))
		i = 1
		while 1:
			data = houses[i*constans.HOUSE_LIST_PAGE_CAPACITY:(i+1)*constans.HOUSE_LIST_PAGE_CAPACITY]
			if data:
				break
			redis_data[str(page+i)] = json.dumps(dict(errno=RET.OK, errmsg="OK", data=data, total_page=total_page))
			i += 1

		redis_key = "hl_%s_%s_%s_%s" % (start_date, end_date, area_id, sort_key)
		try:
			self.redis.hmset(redis_key, redis_data)
		except Exception as e:
			logging.error(e)
			self.redis.delete(redis_key)