# -*- coding:utf-8 -*-
from config import config
from flask_sqlalchemy import SQLAlchemy
from flask import Flask,logging
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
import redis
from utils.common import RegexConverter
from logging.handlers import RotatingFileHandler

redis_store = None
# 开启CSRF防护工能
csrf = CSRFProtect()
# 设置数据库对象
db = SQLAlchemy()
# 开启log日志功能
def login_log(level):
    # 设置⽇志的记录等级
    logging.basicConfig(level=level)  # 调试debug级
    # 创建⽇志记录器，指明⽇志保存的路径、每个⽇志⽂件的最⼤⼤⼩、保存的⽇志⽂件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建⽇志记录的格式 ⽇志等级 输⼊⽇志信息的⽂件名 ⾏数 ⽇志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的⽇志记录器设置⽇志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的⽇志⼯具对象（flask app使⽤的）添加⽇志记录器
    logging.getLogger().addHandler(file_log_handler)


# 工厂方法
def create_app(config_name):
    login_log(config[config_name].LOGGING_LEVEL)  # 根据不同的版本获取BUG等级
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    # 初始化数据库
    db.init_app(app)
    global redis_store
    redis_store = redis.StrictRedis(host=config[config_name].REDIS_HOST, port=config[config_name].REDIS_PORT)
    # 开启Session
    # 设置session保存redis
    Session(app)

    csrf.init_app(app)

    app.url_map.converters['re'] = RegexConverter

    # 注册蓝图：为了解决导入api时，还没有redis_store，造成的ImportError: cannot import name redis_store
    from love_home.api_1_0 import api
    app.register_blueprint(api)

    # 注册静态html文件加载时的蓝图
    from love_home.web_html import html_blue
    app.register_blueprint(html_blue)

    # 的蓝图

    return app