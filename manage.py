# -*- coding:utf-8 -*-
from flask_migrate import Migrate,MigrateCommand
from flask_script import Manager
from love_home import create_app, db


# 创建 app，并传入配置模式：development / production
app = create_app('development')
# 设置脚本对象
manager = Manager(app)
# 设置迁移文件对象
manager.add_command('db', MigrateCommand)
Migrate(app, db)


if __name__ == '__main__':
    print app.url_map
    # manager.run()
    manager.run()