# coding:utf-8
import os

settings = {
	"static_path": os.path.join(os.path.dirname(__file__), "static"),
	"template_path": os.path.join(os.path.dirname(__file__), "template"),
	"cookie_secret": "rn61KEXXTECB+U5XGQxhxitGUUYSYU5PgRP7b4YpFDA=",
	"xsrf_cookies": True,	
	"debug": True
}


mysql_options = {
    "host": "127.0.0.1",
    "database": "ihome",
    "user": "root",
    "password": "123456"
}


redis_options = {
	"host": "127.0.0.1",
	"port": 6379
}


log_file = os.path.join(os.path.dirname(__file__), "logs/log")
log_level = "debug"


# session数据有效期(单位：秒)
session_expires = 86400

# 密码加密salt
passwd_hash_key = "nlgCjaTXQX2jpupQFQLoQo5N4OkEmkeHsHD9+BBx2WQ="

# 七牛图片的域名
image_url_prefix = "http://q5c57mwlu.bkt.clouddn.com"