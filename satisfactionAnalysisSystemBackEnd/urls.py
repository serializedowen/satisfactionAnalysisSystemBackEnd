"""satisfactionAnalysisSystemBackEnd URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from myApp import views

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^login$', views.login, name='login'),
    re_path(r'^logout$', views.logout, name='logout'),
    re_path(r'^user/info$', views.user_info, name='user_info'),
    re_path(r'^user/update$', views.user_update, name='user_update'),
    re_path(r'^data/import$', views.data_import, name='data_import'),
    re_path(r'^dataImport$', views.dataImport, name='data_import'), # 二进制文件上传接口
    re_path(r'^data/list', views.data_list, name='data_list'),  # 数据列表
    re_path(r'^data/info', views.data_info, name='data_info'),  # 数据详情
    re_path(r'^data/del', views.data_del, name='data_del'),  # 数据详删除



    path('', views.index, name='home'),
]
