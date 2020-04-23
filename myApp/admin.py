from django.contrib import admin
from myApp import models
# Register your models here.

# 注册表字段到管理页面
admin.site.register(models.UserInfo)