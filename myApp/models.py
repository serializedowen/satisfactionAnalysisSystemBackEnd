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

class ModelInfo(models.Model):
    mid=models.AutoField(primary_key=True)
    did=models.CharField(max_length=20, verbose_name='数据源id')
    type=models.CharField(max_length=20, verbose_name='模型类型')
    name=models.CharField(max_length=20, verbose_name='名称')
    time=models.CharField(max_length=30, verbose_name='日期')
    # 测量方程变量
    lam=models.TextField(verbose_name='因子载荷')
    error_var_e=models.TextField(verbose_name='误差方差')
    phi=models.TextField(verbose_name='潜变量协方差矩阵')
    # 结构方程变量
    lam_x=models.TextField(verbose_name='内源变量因子载荷')
    lam_y=models.TextField(verbose_name='外源变量因子载荷')
    phi_x=models.TextField(verbose_name='内源潜变量协方差矩阵')
    beta=models.TextField(verbose_name='路径方程外源变量系数')
    gamma=models.TextField(verbose_name='路径方程内源变量系数')
    var_e=models.TextField(verbose_name='路径方程误差方差')
    var_e_x=models.TextField(verbose_name='内源变量误差方差')
    var_e_y=models.TextField(verbose_name='外源变量误差方差')
    #
    lam_y_std1=models.TextField(verbose_name='外源变量的观察变量方差')
    lam_y_std2=models.TextField(verbose_name='外源变量的潜变量方差')
    gamma_x=models.TextField(verbose_name='直接效应')
    gamma_y=models.TextField(verbose_name='中介效应')
    gamma_z=models.TextField(verbose_name='全效应')

    # 留存的字段
    ready_a=models.TextField(verbose_name='全效应')
    ready_b=models.TextField(verbose_name='全效应')
    ready_c=models.TextField(verbose_name='全效应')
    ready_d=models.TextField(verbose_name='全效应')
    ready_e=models.TextField(verbose_name='全效应')

    def __str__(self):
        return self.name

