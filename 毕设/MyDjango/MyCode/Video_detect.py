from django.contrib import admin
from django.urls import path

from django.shortcuts import render
from MyCode.models import UserInfo
from django.shortcuts import HttpResponse  # 导入该模块
from django.contrib import messages


# 一个处理登录的方法
def getHtml(request):
    return render(request, "video_detect.html")