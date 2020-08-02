"""MyDjango URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from MyCode import LoginAccount
from MyCode import Start
from MyCode import GetDarknet
from MyCode import RegisterAccount
from MyCode import Video_detect
from MyCode import Camera_detect
from MyCode import Join
from MyCode import TestCameraDetect
from django.conf.urls import url
urlpatterns = [
    path('admin/', admin.site.urls),
    url(r"^$", Start.index),
    path('login', LoginAccount.login),
    path('register', RegisterAccount.register),
    path('reg', RegisterAccount.getHtml),
    path('join', Join.getHtml),
    path('join_us', Join.register),
    path('video', Video_detect.getHtml),
    path('camera', Camera_detect.getHtml),
    path('video_detect', GetDarknet.video_detect),
    # path('video_detect', TestCameraDetect.video_detect),
    path('camera_savePhotos', GetDarknet.camera_detect),
    path('camera_detect', GetDarknet.getCameraCapacity),
]
