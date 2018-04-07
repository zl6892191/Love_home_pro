# -*- coding:utf-8 -*-
# 实现登录功能
# -*- coding:utf-8 -*-

from . import api
from love_home.modles import User,db
from utils.response_code import RET
from flask import json,request,jsonify,current_app,session
from utils.login_required import login_required

# 设置路由和视图函数
@api.route('/login',methods=['POST'])
def index():
    """
    1.获取账号名和密码
    2.判断参数的完整性
    3.判断与数据库是否相同
    4.保存session信息并跳转到首页
     
    """
    # 获取账号名和密码。
    user_data = request.json
    user_name = user_data.get('username')
    user_pwd = user_data.get('password')
    print '---1---'
    print user_name,user_pwd
    # 判断数据的完整性
    if not all([user_name,user_pwd]):
        return jsonify(errno = RET.PARAMERR,errmsg = u'输入的参数有问题！')
    # 拿到用户的数据库对象
    try:
        user = User.query.filter_by(mobile = user_name).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=u'数据库查询错误')
    # 判断是否有用户
    if not user:
        return jsonify(errno = RET.DATAERR,errmsg =u'账户名或者密码错误！')
    print '---2---'
    # 判断密码是否正确
    if not user.check_password(user_pwd):
        return jsonify(errno = RET.DATAERR,errmsg = u'账户或账户名错误！')

    # 保存session
    session['user_id'] = user.id
    session['name'] = user.name
    session['mobile'] = user.mobile
    return jsonify(errno = RET.OK,errmsg = u'OK')

# 登出


@api.route('/loginout',methods=['DELETE'])
@login_required
def loginout():
    # 获取用户session信息
    session.pop('name')
    session.pop('pwd')
    session.pop('mobile')
    return jsonify(errno=RET.OK,errmsg=u'退出登录成功！')
