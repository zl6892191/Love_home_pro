# coding=utf-8
from flask import session,jsonify,g
from utils.response_code import RET
from functools import wraps

def login_required(view):

    @wraps(view)
    def wapper(*args,**kwargs):
        # 获取user_id
        user_id = session.get('user_id')
        if not user_id:
            print RET.USERERR
            return jsonify(errno = RET.USERERR,errmsg = u'用户未登录！')
        g.user_id = user_id
        return view(*args,**kwargs)
    return wapper
