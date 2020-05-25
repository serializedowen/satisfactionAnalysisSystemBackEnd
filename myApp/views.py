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
from myApp.measurement_model import measurement
from myApp.structural_model import structural

# procession = data_procession.procession


# Create your views here.

def index(request):
    # return HttpResponse('Hello World')
    return render(request, 'myApp/index.html')

# 登录接口
def login(request):
    try:
        if request.method == 'GET':
            return HttpResponse(json.dumps({
                "status": False
            }), content_type="application/json")
        else:
            print(request.body)
            # 前端通过json来传输参数，所以这里通过json.loads转化格式
            params = json.loads(request.body.decode('utf-8'))

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
    except Exception as e:
        print(e)

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
        params = json.loads(request.body.decode('utf-8'))
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
        params = json.loads(request.body.decode('utf-8'))
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
        res = list(models.DataInfo.objects.values("uid", "displayName", "time", "url").order_by('-uid'))
        return HttpResponse(json.dumps({
            "status": True,
            "data": res
        }))
    return HttpResponse(json.dumps({
        "status": False,
    }))

def data_info(request):
    if request.method == 'POST':
        params = json.loads(request.body.decode('utf-8'))
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


def model_submit(request):
    if request.method == 'POST':
        params = json.loads(request.body.decode('utf-8'))
        dataSource = params.get('dataSource', None)
        lam = params.get('lam', None)
        method = params.get('method', None)
        step = params.get('step', None)
        max_iter = params.get('max_iter', None)
        rdd = params.get('rdd', None)
        type = params.get('type', None)
        name = params.get('name', None)

        x = params.get('x', None)
        y = params.get('y', None)
        lam_x = params.get('lam_x', None)
        lam_y = params.get('lam_y', None)
        beta = params.get('beta', None)
        gamma = params.get('gamma', None)

        base_path = list(models.DataInfo.objects.filter(uid=dataSource).values("url"))

        if dataSource and lam and method and step and max_iter and rdd and type and name and type == 'measurement':
            time_ = time.strftime('%b %d %Y %H:%M:%S')
            result = measurement(base_path[0]['url'],eval(lam), step, max_iter, rdd)
            print(result)
            if result['status']:
                models.ModelInfo.objects.create(
                    did=dataSource,
                    type=type,
                    name=name,
                    time=time_,
                    lam=result['lam'],
                    error_var_e=result['error_var_e'],
                    phi=result['phi'],
                    ready_a=True,
                )
                return HttpResponse(json.dumps({
                    "status": True,
                }))
            else:
                models.ModelInfo.objects.create(
                    did=dataSource,
                    type=type,
                    name=name,
                    time=time_,
                    ready_a=False,
                    ready_b=result['msg']
                )
                print('运行失败')

        if dataSource and gamma and beta and x and y and lam_x and lam_y and method and step and max_iter and type and name and type == 'structural':
            time_ = time.strftime('%b %d %Y %H:%M:%S')
            result = structural(base_path[0]['url'], eval(y), eval(x), eval(lam_x), eval(lam_y), eval(beta), eval(gamma), method, step, max_iter)
            print(result)
            if result['status']:
                models.ModelInfo.objects.create(
                    did=dataSource,
                    type=type,
                    name=name,
                    time=time_,
                    lam_x=result['lam_x'],
                    lam_y=result['lam_y'],
                    phi_x=result['phi_x'],
                    beta=result['beta'],
                    gamma=result['gamma'],
                    var_e=result['var_e'],
                    var_e_x=result['var_e_x'],
                    var_e_y=result['var_e_y'],
                    ready_a=True,
                )
                return HttpResponse(json.dumps({
                    "status": True,
                }))
            else:
                models.ModelInfo.objects.create(
                    did=dataSource,
                    type=type,
                    name=name,
                    time=time_,
                    ready_a=False,
                    ready_b=result['msg']
                )
                print('运行失败')


    return HttpResponse(json.dumps({
        "status": False,
    }))


def model_list(request):
    if request.method == 'GET':

        data_list = list(models.DataInfo.objects.values("uid").order_by('-uid'))

        data_uid_list = []
        if data_list:
            for uid_item in data_list:
                data_uid_list.append(uid_item['uid'])
        model_lists = list(models.ModelInfo.objects.values("mid", "did", "type", "name", "time", "ready_a", "ready_b").order_by('-mid'))

        res = {}
        for uid in data_uid_list:
            model_item_list = []
            for model in model_lists:
                if model['did'] == str(uid):
                    model_item_list.append(model)
            res[str(uid)] = model_item_list
        return HttpResponse(json.dumps({
            "status": True,
            "data": res
        }))

    return HttpResponse(json.dumps({
        "status": False,
    }))


def model_del(request):
    if request.method == 'GET':
        mid = request.GET.get('mid', None)
        result = models.ModelInfo.objects.filter(mid=mid).delete()
        return HttpResponse(json.dumps({
            "status": True,
            "data": "删除成功"
        }))
    return HttpResponse(json.dumps({
        "status": False,
    }))



def model_info(request):
    if request.method == 'GET':
        mid = request.GET.get('mid', None)
        result = list(models.ModelInfo.objects.filter(mid=mid).values())
        if result:
            return HttpResponse(json.dumps({
                "status": True,
                "data": result[0]
            }))
    return HttpResponse(json.dumps({
        "status": False,
    }))