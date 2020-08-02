from django.shortcuts import render
from django.shortcuts import HttpResponse  # 导入该模块
# Create your views here.


# 编写在路由中定义的index函数，参数为request
# (request 封装了用户请求的所有内容)
def index(request):
    return render(request, "Login.html")

