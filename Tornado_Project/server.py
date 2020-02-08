# coding:utf-8

import tornado.web
import tornado.ioloop
import tornado.options
import tornado.httpserver
import os
import torndb
import config
import redis as rds

from handlers import Passport
from urls import handlers
from tornado.options import options, define
from tornado.web import RequestHandler

define("port", default=8000, type=int, help="run server on the given port")


class Application(tornado.web.Application):
    def __init__(self, *args, **kwargs):
        super(Application, self).__init__(*args, **kwargs)
        self.db = torndb.Connection(**config.mysql_options)
        self.redis = rds.StrictRedis(**config.redis_options)


def main():
    options.log_file_prefix = config.log_file
    options.logging = config.log_level
    tornado.options.parse_command_line()
    app = Application(
        handlers,
        **config.settings
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()
    # jjjjj