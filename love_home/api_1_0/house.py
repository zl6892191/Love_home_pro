# coding=utf-8
from . import api
from love_home.modles import Area,House,Facility,HouseImage,constants
from utils.response_code import RET
from flask import jsonify,request,current_app,g
from utils.login_required import login_required
from love_home import db
from utils.image_storage import upload_image


@api.route('/areas')
def area():
    """
    1. 获取数据库数据
    2. 遍历数据
    3. 显示数据
    """
    areas = Area.query.all()
    # areas_dict = []
    # adi_list = []
    # aname_list = []
    # for area_info in areas:
    #     adi = area_info.id
    #     # adi_list.append(adi)
    #     aname = area_info.name
    #     # aname_list.append(aname)
    #     # diction = dict(zip(adi_list,aname_list))
    #     # areas_dict.append(diction)
    # print areas_dict
    area_dict_list = []
    for area in areas:
        area_dict_list.append(area.to_dict())
    return jsonify(errno=RET.OK ,errmsg = u'获取成功！',data = area_dict_list)


# 发布新房源
@api.route('/houses',methods=['POST'])
@login_required
def house():
    """
    1. 获取所有房屋参数
    2. 校验参数的完整性
    3. 存入数据库
    
    :return: 
    """
    # 接受参数并校验
    json_dict = request.json

    title = json_dict.get('title')
    price = json_dict.get('price')
    address = json_dict.get('address')
    area_id = json_dict.get('area_id')
    room_count = json_dict.get('room_count')
    acreage = json_dict.get('acreage')
    unit = json_dict.get('unit')
    capacity = json_dict.get('capacity')
    beds = json_dict.get('beds')
    deposit = json_dict.get('deposit')
    min_days = json_dict.get('min_days')
    max_days = json_dict.get('max_days')

    if not all(
            [title, price, address, area_id, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')

    # 判断价格和押金数是否是数字
    try:
        price = int(float(price) * 100)  # 0.1元 ==> 10分
        deposit = int(float(deposit) * 100)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数格式错误')

    # 存入数据库
        # 3.实例化房屋模型对象，并给属性赋值
    house = House()
    house.user_id = g.user_id
    house.area_id = area_id
    house.title = title
    house.price = price
    house.address = address
    house.room_count = room_count
    house.acreage = acreage
    house.unit = unit
    house.capacity = capacity
    house.beds = beds
    house.deposit = deposit
    house.min_days = min_days
    house.max_days = max_days

    # 处理房屋的设施 facilities = [2,4,6]
    facilities = json_dict.get('facility')
    # 查询出被选中的设施模型对象
    house.facilities = Facility.query.filter(Facility.id.in_(facilities)).all()

    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno = RET.DBERR,errmsg = u'保存数据库失败！')
    return jsonify(errno=RET.OK,errmsg='OK',data={'house_id' : house.id})


# 处理上传图像
@api.route('/houses/image',methods=['POST'])
@login_required
def house_image():
    """
    1.获取图片信息
    2.调用七牛上传照片
    3.拿到地址上传到数据库
    4.响应数据给前段
    """
    # 获取图片
    try:
        image = request.files.get('house_image')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR,errmsg = u'参数错误！')
    # 查询房屋ID
    try:
        house_id = request.form.get('house_id')
        houses = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg=u'查询数据失败')
    if not houses:
        return jsonify(errno =RET.NODATA,errmsg=u'房屋不存在！')
    # 调用七牛云图片上传
    try:
       key = upload_image(image)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR,errmsg=u'上传图片失败！')
    # 将图片保存到数据库
    house_images = HouseImage()
    house_images.house_id = house_id
    house_images.url = key
    # 选择一个图片，作为房屋的默认图片
    if not houses.index_image_url:
        houses.index_image_url = key

    try:
        db.session.add(house_images)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='存储房屋图片失败')

    # 5.响应结果：上传的房屋图片，需要立即刷新出来
    image_url = constants.QINIU_DOMIN_PREFIX + key
    print image_url
    return jsonify(errno=RET.OK, errmsg='发布房屋图片成功', data={'image_url': image_url})


