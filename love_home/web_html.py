# -*- coding:utf-8 -*-
from flask import Blueprint,current_app,make_response
from flask_wtf.csrf import generate_csrf

html_blue = Blueprint('html_blue', __name__)

@html_blue.route('/<re(".*"):file_name>')
def get_static_html(file_name):
    if not file_name:
        file_name = 'index.html'

    if file_name != 'favicon.ico':
        file_name = 'html/'+ file_name
    # 设置csrf的信息
    rsponse = make_response(current_app.send_static_file(file_name))
    token = generate_csrf()
    rsponse.set_cookie('csrf_token',token)
    return rsponse