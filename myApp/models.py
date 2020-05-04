from django.db import models

# Create your models here.

class UserInfo(models.Model):
    uid=models.AutoField(primary_key=True)
    name=models.CharField(max_length=20, verbose_name='用户名')
    username=models.CharField(max_length=20,unique=True,verbose_name='账号') # 用户名唯一
    password=models.CharField(max_length=12,verbose_name='密码')
    def __str__(self):
        return self.username

class DataInfo(models.Model):
    uid=models.AutoField(primary_key=True)
    displayName=models.CharField(max_length=20, verbose_name='展示名')
    time=models.CharField(max_length=30, verbose_name='日期')
    url=models.CharField(max_length=50, verbose_name='url')
    score_obj=models.CharField(max_length=100, verbose_name='选项和分值的对应关系')
    titleRangeStart=models.CharField(max_length=20, verbose_name='表头开始地址')
    titleRangeEnd=models.CharField(max_length=20, verbose_name='表头结束地址')
    chooseRangeStart=models.CharField(max_length=20, verbose_name='选项开始地址')
    chooseRangeEnd=models.CharField(max_length=20, verbose_name='选项结束地址')
    xRangeStart=models.CharField(max_length=20, verbose_name='x指标开始地址')
    xRangeEnd=models.CharField(max_length=20, verbose_name='x指标结束地址')
    yRangeStart=models.CharField(max_length=20, verbose_name='y指标开始地址')
    yRangeEnd=models.CharField(max_length=20, verbose_name='y指标结束地址')
    titleList=models.TextField(verbose_name='表头列表')
    xyRange=models.TextField(verbose_name='处理后数据')
    def __str__(self):
        return self.displayName
