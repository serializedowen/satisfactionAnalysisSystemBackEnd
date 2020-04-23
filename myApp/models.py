from django.db import models

# Create your models here.

class UserInfo(models.Model):
    uid=models.AutoField(primary_key=True)
    name=models.CharField(max_length=20, verbose_name='用户名')
    username=models.CharField(max_length=20,unique=True,verbose_name='账号') # 用户名唯一
    password=models.CharField(max_length=12,verbose_name='密码')
    def __str__(self):
        return self.username

