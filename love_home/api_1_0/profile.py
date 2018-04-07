# -*- coding:utf-8 -*-


from . import api
from flask import request,current_app,jsonify,g
from utils.response_code import RET
from utils.image_storage import upload_image
from love_home import constants,db
from love_home.modles import User
from utils.login_required import login_required

# 获取用户
@api.route('/users')
@login_required
def user():
    """
    0.判断是否登录
    1.获取当前的ID
    2.查出ID的相关信息
    3.构造相应数据
    4.响应数据
    """
    # 获取当前ID
    user_id = g.user_id
    # 查出想关的数据信息
    print user_id
    try:
        user_info = User.query.get( user_id)
        print user_info
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno = RET.DBERR,errmsg = u'查询失败！')
    if not user_info:
        return jsonify(errno = RET.DATAERR,errmsg=u'用户不存在！')
    response_data = user_info.to_dict()
    return jsonify(errno = RET.OK,errmsg = u'OK',data = response_data)

# 上传图片
@api.route('/avatar',methods = ['POST'])
@login_required
def profile():
    """
    1.获取图片
    2.调用七牛云上传图片
    3.拿到图片存储地址
    """
    # 获取图片
    try:
        avater_file = request.files.get('avatar').read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno = RET.DATAERR,errmsg = u'图片数据有错！')

    # 调用七牛上传图片
    try:
        key = upload_image(avater_file)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='上传头像失败')

    # 更新当前用户的头像地址

    user_id = g.user_id
    try:

        use = User.query.get(user_id)
        use.avatar_url = key
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='图片保存失败')

    key = constants.QINIU_DOMIN_PREFIX + key
    print key
    return jsonify(errno = RET.OK,errmsg='OK',data = key)


# 保存用户名
@api.route('/from_name',methods = ['PUT'])
@login_required
def from_name():
    # 获取更改信息
    user_dict = request.json
    user_name = user_dict.get('username')

    # 根据ID查出信息
    user_id = g.user_id

    try:
        use = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno = RET.USERERR,errmsg=u'查无此人!')
    use.name = user_name
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg = u'修改用户名失败！')
    return jsonify(erron = RET.OK,errmsg='ok')

# 实名认证
@api.route('/users/auth', methods=['POST'])
@login_required
def set_user_auth():
    """提供用户实名认证
    0.判断用户是否是登录用户 @login_required
    1.接受参数：real_name , id_card
    2.判断参数是否缺少：这里就不对身份证进行格式的校验，省略掉
    3.查询当前的登录用户模型对象
    4.将real_name , id_card赋值给用户模型对象
    5.将新的数据写入到数据库
    6.响应结果
    """

    # 1.接受参数：real_name , id_card
    json_dict = request.json
    real_name = json_dict.get('real_name')
    id_card = json_dict.get('id_card')

    # 2.判断参数是否缺少：这里就不对身份证进行格式的校验，省略掉
    if not all([real_name, id_card]):
        return jsonify(errno=RET.PARAMERR, errmsg='缺少参数')

    # 3.查询当前的登录用户模型对象
    user_id = g.user_id
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询用户数据失败')
    if not user:
        return jsonify(errno=RET.NODATA, errmsg='用户不存在')

    # 4.将real_name , id_card赋值给用户模型对象
    user.real_name = real_name
    user.id_card = id_card

    # 5.将新的数据写入到数据库
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存实名认证数据失败')

    # 6.响应结果
    return jsonify(errno=RET.OK, errmsg='实名认证成功')