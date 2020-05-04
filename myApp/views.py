from django.shortcuts import render
from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseRedirect
from django.http import HttpResponse
from django.contrib import auth
from myApp import  models
import time
import copy
import json
from myApp.data_procession import procession

# procession = data_procession.procession


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

# 文件上传个解析
def data_import(request):
    if request.method == "POST":
        print(request.FILES)
        params = json.loads(request.body)
        dataFile = params.get('dataFile', None)
        displayName = params.get('displayName', None)

        dataFile_name = dataFile[0]['name']
        score_obj = params.get('score_obj', None)
        titleRangeStart = params.get('titleRangeStart', None)
        titleRangeEnd = params.get('titleRangeEnd', None)
        chooseRangeStart = params.get('chooseRangeStart', None)
        chooseRangeEnd = params.get('chooseRangeEnd', None)
        xRangeStart = params.get('xRangeStart', None)
        xRangeEnd = params.get('xRangeEnd', None)
        yRangeStart = params.get('yRangeStart', None)
        yRangeEnd = params.get('yRangeEnd', None)

        url = 'static/files/' + dataFile_name
        res = procession(url, score_obj, titleRangeStart, titleRangeEnd, chooseRangeStart, chooseRangeEnd, xRangeStart, xRangeEnd, yRangeStart, yRangeEnd)
        titleList = res.get('titleList', None)
        xyRange= res.get('xyRange', None)
        time_ = time.strftime('%b %d %Y %H:%M:%S')
        # 数据处理完成
        if res:
            models.DataInfo.objects.create(
                displayName=displayName,
                url=url,
                score_obj=score_obj,
                titleRangeStart=titleRangeStart,
                titleRangeEnd=titleRangeEnd,
                chooseRangeStart=chooseRangeStart,
                chooseRangeEnd=chooseRangeEnd,
                xRangeStart=xRangeStart,
                xRangeEnd=xRangeEnd,
                yRangeStart=yRangeStart,
                yRangeEnd=yRangeEnd,
                titleList=titleList,
                xyRange=xyRange,
                time=time_,
            )
            return HttpResponse(json.dumps({
                "status": True,
                "data": {
                    "msg": "数据导入成功"
                }
            }))
        else:
            return HttpResponse(json.dumps({
                "status": False,
            }))



def handle_uploaded_file2(f,url):
    with open(url, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return True

def dataImport(request):
    url = 'static/files/' + request.FILES.get('files').name
    res = handle_uploaded_file2(request.FILES['files'], url)
    if (res):
        return HttpResponse(json.dumps({
            "status": True,
        }))
    else:
        return HttpResponse(json.dumps({
            "status": False,
        }))


def data_list(request):
    if request.method == 'GET':
        res = list(models.DataInfo.objects.values("uid", "displayName", "time", "url"))
        return HttpResponse(json.dumps({
            "status": True,
            "data": res
        }))
    return HttpResponse(json.dumps({
        "status": False,
    }))

def data_info(request):
    if request.method == 'POST':
        params = json.loads(request.body)
        uid = params.get('uid', None)
        res = list(models.DataInfo.objects.filter(uid=uid).values())[0]
        print(res['titleList'])
        title_list = eval(res['titleList'])
        res_title = []
        for i in range(len(title_list)):
            item = {}
            item["title"] = title_list[i]
            item["dataIndex"] = 'X' + str(i +1)
            item["key"] = 'X' + str(i +1)
            item["width"] = 120
            res_title.append(item)

        xy_range = eval(res['xyRange'])
        res_data=[]
        res_title2 = copy.deepcopy(res_title)
        for row in range(len(xy_range)):
            res_item = {}
            res_item["key"] = row
            print(xy_range[row])
            for item in range(len(xy_range[row])):
                # x
                key = ''
                if(item < len(res_title2)):
                    key = 'X' + str(item + 1)
                else:
                    key = 'Y' + str(item - len(res_title2) + 1)
                    if len(res_title) < len(xy_range[row]):
                        res_title.append({
                            "title": "满意度",
                            "dataIndex": key,
                            "key": key,
                            "width": 120
                        })
                res_item[key] = xy_range[row][item]
            res_data.append(res_item)


        return HttpResponse(json.dumps({
            "status": True,
            "data": {
                "res_title": res_title,
                "res_data": res_data
            }
        }))
    return HttpResponse(json.dumps({
        "status": False,
    }))


def data_del(request):
    if request.method == 'GET':
        uid = request.GET.get('uid', None)
        result = models.DataInfo.objects.filter(uid=uid).delete()
        return HttpResponse(json.dumps({
            "status": True,
            "data": "删除成功"
        }))
    return HttpResponse(json.dumps({
        "status": False,
    }))