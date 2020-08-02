from django.contrib import admin
from django.urls import path

from django.shortcuts import render
from MyCode.models import UserInfo
from django.shortcuts import HttpResponse  # 导入该模块
from django.contrib import messages


# 一个处理注册的方法
def register(request):
    # 接收用户在页面上的userid,userpwd两个文本框中的值
    flag = 0
    if request.method == "POST":
        username = request.POST.get('account')
        password = request.POST.get('password')
        confirm = request.POST.get('confirm')
        if username == "" or password == "" or confirm == "":
            flag = 0  # 表示账号密码为空
        else:
            if confirm == password:
                if UserInfo.objects.filter(username=username).first():
                    flag = 3
                else:
                    if UserInfo.objects.create(username=username, password=password):
                        flag = 1
                    else:
                        flag = 2
            else:
                flag = -1  # 表示账号密码不对

    if flag == 1:
        messages.error(request, '注册成功')
        return render(request, "Login.html")
    else:
        if flag == -1:
            messages.error(request, '注册失败,两次密码不一致')
        else:
            if flag == 0:
                messages.error(request, "账号、密码及确认密码不能为空")
            else:
                if flag == 3:
                    messages.error(request, "注册失败,账号已存在")
                else:
                    messages.error(request, "注册失败,发生了未知错误")

        return render(request, "Register.html")
    # return render(request,"index.html")


# 一个处理登录的方法
def getHtml(request):
    return render(request, "Register.html")
