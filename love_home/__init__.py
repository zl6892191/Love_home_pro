# -*- coding:utf-8 -*-
from config import config
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
import redis

redis_store = None
# 开启CSRF防护工能
csrf = CSRFProtect()
# 设置数据库对象
db = SQLAlchemy()
# 工厂方法
def create_app(config_name):
    app = Flask(__name__)
    # 设置DEBUG 导入模式
    app.config.from_object(config[config_name])
    # 初始化数据库
    db.init_app(app)
    global redis_store
    redis_store = redis.StrictRedis(host=config[config_name].REDIS_HOST, port=config[config_name].REDIS_PORT)
    # 开启Session
    # 设置session保存redis
    Session(app)

    csrf.init_app(app)
    return app