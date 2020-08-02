from django.db import models

# Create your models here.
from django.db import models


# 定义图书模型类BookInfo
class UserInfo(models.Model):
    username = models.CharField(max_length=255, primary_key=True)
    password = models.CharField(max_length=255)

    class Meta:
        db_table = 'users'  # 指明数据库表名
        verbose_name = '用户'  # 在admin站点中显示的名称
        verbose_name_plural = verbose_name  # 显示的复数名称

    def __str__(self):
        """定义每个数据对象的显示信息"""
        return self.username


class ManagerInfo(models.Model):
    username = models.CharField(max_length=255, primary_key=True)
    password = models.CharField(max_length=255)

    class Meta:
        db_table = 'managers'  # 指明数据库表名
        verbose_name = '管理员'  # 在admin站点中显示的名称
        verbose_name_plural = verbose_name  # 显示的复数名称

    def __str__(self):
        """定义每个数据对象的显示信息"""
        return self.username


