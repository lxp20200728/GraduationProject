from django.contrib import admin
from django.urls import path

from django.shortcuts import render
from MyCode.models import UserInfo
from MyCode.models import ManagerInfo
from django.shortcuts import HttpResponse  # 导入该模块
from django.contrib import messages
from MyCode import Camera_detect
from MyCode import GetDarknet
import os


# 一个处理注册的方法
def login(request):
    # 接收用户在页面上的userid,userpwd两个文本框中的值
    if request.method == "POST":
        username = request.POST.get('account')
        password = request.POST.get('password')
        type = request.POST.get('user')
        filePath = os.path.dirname(__file__)  # 获取工程运行时路径
        filePath = filePath.replace("\\", '/')
        user_obj = False
        if type == "users":
            if username == "" or password == "":
                messages.error(request, '账号密码不能为空,请重新输入')
                return render(request, "Login.html")
            else:
                user_obj = UserInfo.objects.filter(username=username, password=password).first()
                if user_obj:
                    Camera_detect.changePermission(False)
                    GetDarknet.saveCachePath(filePath + '/MyCache/' + str(username))
                    messages.error(request, '登录成功')
                    return render(request, "Main.html")
        else:
            if username == "" or password == "":
                messages.error(request, '账号密码不能为空,请重新输入')
                return render(request, "Login.html")
            else:
                user_obj = ManagerInfo.objects.filter(username=username, password=password).first()
                if user_obj:
                    Camera_detect.changePermission(True)
                    GetDarknet.saveCachePath(filePath + '/MyCache/' + str(username))
                    messages.error(request, '登录成功')
                    return render(request, "Main.html")
        messages.error(request, '用户名或密码错误,请重新登录')
        return render(request, "Login.html")
    # return render(request,"index.html")

