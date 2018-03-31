# coding=utf-8
import redis


class Config(object):

    # 链接数据库mysql
    SQLALCHEMY_DATABASE_URI = "mysql://test1:666666@192.168.44.160:3306/love_home"
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 关闭数据库追踪
    REDIS_HOST = "192.168.44.160"  # redis 服务器地址
    REDIS_PORT = 6379  # redis 服务器端口
    # 设置 session加密规则
    SECRET_KEY = "EjpNVSNQTyGi1VvWECj9TvC/+kq3oujee2kTfQUs8yCM6xX9Yjq52v54g+HVoknA"
    SESSION_TYPE = "redis"  # 设置session保存模式
    SESSION_USE_SIGNER = True  # 使用 redis 的实例
    PERMANENT_SESSION_LIFETIME = 3600 * 24  # session 的有效期，单位是秒
    redis_store = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)


# 开发模式配置
class DevelopementConfig(Config):
    DEBUG = True  # 开启BUG模式

# 生产模式配置
class ProductionConfig(Config):
    pass


config = {
    "development": DevelopementConfig,
    "production": ProductionConfig
}