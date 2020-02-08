# coding:utf-8
import os

from handlers import Passport, VerifyCode, house, profile
from handlers.BaseHandler import StaticFileHandler


handlers = [
	(r'/api/smscode', VerifyCode.SMSCodeHandler),
	(r'/api/imagecode', VerifyCode.ImageCodeHandler),
	(r'^/api/register$', Passport.RegisterHandler),
	(r'^/api/login$', Passport.LoginHandler),
	(r'^/api/check_login$', Passport.CheckLoginHandler),
	(r'^/api/profile/avatar$', Passport.AvatarHandler),
	(r'^/api/house/area$', house.AreaInfoHandler),
	(r'^/api/house/my$', house.MyHouseHandler),
	(r'/(.*)', StaticFileHandler, dict(path=os.path.join(os.path.dirname(__file__), "html"), default_filename="index.html"))
]