# -*- coding:utf-8 -*-
import re
import random
from love_home.api_1_0 import api
from utils.captcha.captcha import captcha
from flask import request,make_response,json,jsonify,current_app
from love_home import redis_store,db
from love_home.modles import User
from love_home import constants
from utils.response_code import RET
from utils.SendTemplateSMS import sendTemplateSMS

@api.route('/image_code')
def git_image_code():

    # 获取验证码
    name,text,image = captcha.generate_captcha()
    # 获取数据UUID
    uuid = request.args.get('uuid')
    after_id = request.args.get('after_id')
    print uuid
    redis_store.set('imagecode:'+uuid,text,constants.IMAGE_CODE_REDIS_EXPIRES)
    # 判断是否有after_id的数据，有则删除
    if after_id:
        a = 'imagecode:'+after_id
        redis_store.delete(a)
    resp = make_response(image)
    resp.headers['Content-Type'] = 'image/jpg'
    return resp

# 短信验证功能
@api.route('/smscode',methods = ['POST'])
def send_sms_code():
    """
    1.获取手机号码，图片验证码，和uuid
    2.判断参数是否完整，
    3.判断手机号是否合法
    4.判断用户输入的验证码是和数据库的相同
    5.获取sms平台对象和模板
    6.给手机号码发送短信验证码
    """
    # 获取参数，手机号，验证码和uuid。data是原始字符串Json
    global stringcode
    data = request.data
    print '---1---'
    print data
    # 将Json装换成已操作的字符串
    data_dict = json.loads(data)
    print '---2---'
    print data_dict
    mobile = data_dict.get('mobile')
    image_code = data_dict.get('imagecode')
    uuid = data_dict.get('uuid')
    # 判断数据的完整性
    if not all([mobile,image_code,uuid]):
        return jsonify(errno = RET.PARAMERR, errmsg = u'缺少参数！')
    print '---3---'
    # 判断手机号码是否正确
    if not re.match(r'^(0|86|17951)?(13[0-9]|15[012356789]|17[013678]|18[0-9]|14[57])[0-9]{8}$',mobile):
        return jsonify(errno = RET.PARAMERR, errmsg = u'手机格式不正确！')
    print '---4---'
    # 获取uuid里面的验证码
    try:
        stringcode = redis_store.get('imagecode:'+ uuid)
    except Exception as e:
        current_app.logger.error(e)
    # 判断数据库是否有数据
    print '---5---'
    if not stringcode:
        return jsonify(errno = RET.NODATA,errmsg = u'验证码不存在！')
    print '---6---'
    if image_code != stringcode:
        return jsonify(errno = RET.DATAERR,errmsg = u'验证码不正确！')
    # 生成随机数据
    sms_numb = '%06d'% random.randint(0,999999)
    current_app.logger.debug('短信验证码为：' + sms_numb)
    # 验证完成，开始准备数据发送验证码
    print '---7---'
    result=sendTemplateSMS('13922121005', [sms_numb, '5'], '1')
    if result.get('statusCode') != '000000':
        return jsonify(errno = RET.SERVERERR, errmsg = u'短信验证码发送失败！')
    # 保存验证到数据库
    print '---8---'
    redis_store.set('Mobile:'+ mobile,sms_numb,constants.SMS_CODE_REDIS_EXPIRES)
    return jsonify(errno = RET.OK, errmsg = u'短信发送成功！' )


# 用户注册接口实现register
@api.route('/register',methods = ['POST'])
def register():
    """
    1.拿到ajax传过来的数据
    2.判断数据的完整性
    3.判断短信验证码是否与数据库相同
    4.判断两次密码是否相同
    5.点击注册，将手机，用户名和密码存入数据库
    
    """
    # 拿到前端的数据
    # global mobile_val
    json_dict = request.json
    mobile = json_dict.get('mobile')
    sms_code = json_dict.get('sms_code')
    password = json_dict.get('password')
    # 判断数据的完整性
    if not all([mobile,sms_code,password]):
        return jsonify(errno = RET.PARAMERR,errmsg = u'参数不完整！')
    # 对比数据库短信验证码是否相同
    keys = 'Mobile:' + mobile
    try:
        mobile_val = redis_store.get(keys)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno = RET.NODATA,errmsg = u'无效的参数！')
    if mobile_val != sms_code:
        return jsonify(errno = RET.DATAERR,errmsg = u'验证码不匹配！')
    # 数据保存到数据库
    user = User()
    user.name = mobile
    user.mobile = mobile
    user.password = password
    # 尝试提交
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno = RET.SERVERERR,errmsg = u'数据保存失败！')

    return jsonify(errno = RET.OK,errmsg = u'用户注册成功！')
