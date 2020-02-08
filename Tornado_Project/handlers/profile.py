# coding:utf-8

import logging

from .BaseHandler import BaseHandler
from utils.image_storage import storage
from utils.response_code import RET
from utils.common import required_logined
from config import image_url_prefix


class AvatarHandler(BaseHandler):
	""""""
	@require_logined
	def post(self):
		user_id = self.session.data["user_id"]
		try:
			avatar = self.request.files["avatar"][0]["body"]
		except Exception as e:
			logging.error(e)
			return self.write(dict(errno=RET.PARAMERR, errmsg="参数错误"))

		try:
			img_name = storage(image_data)
		except Exception as e:
			logging.error(e)
			img_name = None

		if not img_name:
			return self.write(dict(errno=RET.THIRDERR, errmsg="qiniu error"))

		try:
			ret = self.db.execute("update ih_user_profile set up_avatar=%(avatar)s where up_user_id=%(user_id)s", avatar=img_name, user_id=user_id)
		except Exception as e:
			logging.error(e)
			return self.write(dict(errno=RET.DBERR, errmsg="upload failed"))
			
		img_url = image_url_prefix + img_name
		self.write(dict(errno=RET.OK, errmsg="OK", url=img_url))