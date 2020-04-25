from django.shortcuts import render
from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseRedirect
from django.http import HttpResponse
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
            return HttpResponse(json.dumps({
                "status": True,
                "data": {
                    "name": result['name'],
                    "uid": result['uid']
                }
            }))
        return HttpResponse(json.dumps({
            "status": False,
            "data": 'admin'
        }))