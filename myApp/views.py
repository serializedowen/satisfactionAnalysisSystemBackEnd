from django.shortcuts import render
from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseRedirect
from django.http import HttpResponse
from django.contrib import auth
from myApp import  models
import json


# Create your views here.

def index(request):
    # return HttpResponse('Hello World')
    return render(request, 'myApp/index.html')

# 登录接口
def login(request):
    if request.method == 'GET':
        return HttpResponse(json.dumps({
            "status": False
        }), content_type="application/json")
    else:
        # 前端通过json来传输参数，所以这里通过json.loads转化格式
        params = json.loads(request.body)

        userInfo = models.UserInfo.objects.filter(username=params.get('username', None), password=params.get('password', None))
        if userInfo:
            result = list(userInfo.values())[0]
            print(result)

            res_data =  {
                    "name": result['name'],
                    "uid": result['uid'],
                    "username": result['username']
                }


            res = HttpResponse(json.dumps({
                "status": True,
                "data": res_data
            }))

            request.session['user_id'] = res_data
            # res.set_cookie("samesite", "None")

            return res
        return HttpResponse(json.dumps({
            "status": False,
            "data": 'admin'
        }))

# 登出接口
def logout(request):
    if request.method == 'GET':
        user = request.session.get('user_id', False)
        # session 存在则删除
        if user:
            del request.session['user_id']
            return HttpResponse(json.dumps({
                "status": True,
                "data": "退出登录成功！"
            }))
        else:
            return HttpResponse(json.dumps({
                "status": False,
                "data": "退出登录失败！"
            }))


# 获取用户信息
def user_info(request):
    if request.method == 'GET':
        user = request.session.get('user_id', False)
        print(user)
        if user:
            return HttpResponse(json.dumps({
                "status": True,
                "data": {
                    "uid": user['uid'],
                    "name": user['name'],
                    "username": user['username']
                }
            }))
        else:
            return HttpResponse(json.dumps({
                "status": False,
            }))
    else:
        return HttpResponse(json.dumps({
            "status": False,
        }))


# 更新用户信息
def user_update(request):
    user = request.session.get('user_id', False)
    if request.method == 'POST' and user:
        params = json.loads(request.body)
        name = params.get('name', None)
        username = params.get('username', None)
        password = params.get('password', None)

        result = models.UserInfo.objects.filter(
            username=username
        ).update(
            name=name,
            password=password
        )
        if result:
            res_data = {
                "uid": user['uid'],
                "name": name,
                "username": username
            }

            res = HttpResponse(json.dumps({
                "status": True,
                "data": res_data
            }))
            request.session['user_id'] = res_data
            return res
    return HttpResponse(json.dumps({
        "status": False,
    }))