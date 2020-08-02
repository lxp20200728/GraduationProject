from django.contrib import admin
from django.urls import path
from django.contrib import messages
from django.shortcuts import render
from MyCode.models import UserInfo
from django.shortcuts import HttpResponse  # 导入该模块
from django.contrib import messages


permission = False


# 一个处理登录的方法
def getHtml(request):
    if permission:
        return render(request, "camera_detect.html")
    else:
        messages.error(request, '该功能需要管理员权限')
        return render(request, "video_detect.html")


def changePermission(type):
    global permission
    permission = type
