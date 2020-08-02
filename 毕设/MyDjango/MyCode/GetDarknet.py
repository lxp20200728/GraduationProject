from django.contrib import admin
from django.urls import path
#from moviepy.editor import *
import cv2
import os
import time
import datetime
import base64
import threading
import json
from django.contrib import messages
from django.shortcuts import render
from django.shortcuts import HttpResponse  # 导入该模块
from darknet import darknet
from MyCode import GetCapacity

net, meta = darknet.loadModle()  # 加载模型
cachePath = "/home/lxp/PycharmProjects/MyDjango/MyCode/MyCache/lxp"


def video_detect(request):  # 视频检测
    capacityA = []
    capacityB = []
    if request.method == "POST":
        print("begin")
        videoPath = request.FILES['video'].temporary_file_path()  # 获取视频临时路径
        f1 = open('data1.txt', "w")
        f2 = open('data2.txt', "w")
        imagesPaths, times = getImgsPath(videoPath)  # 视频提取帧并返回图片路径与时间
        trashCanA = []
        trashCanB = []
        count = 0
        i = 0
        while i < len(imagesPaths):  # 对图片进行循环
            if not saveTxt(imagesPaths[i], darknet.detect(net, meta, imagesPaths[i]), times[i], trashCanA,
                           trashCanB):  # 判断是否检测到垃圾桶
                count = count + 1
                begin = False
            else:
                begin = True
                count = 0
            if (not begin) and count > 5:  # 连续5次检测不到，进行跳跃式检测
                index = i
                while index + 10 < len(imagesPaths) and len(
                        darknet.detect(net, meta, imagesPaths[index + 10])) < 1:  # 每隔一秒判断一次,寻找下一个起始点
                    index = index + 10
                i = index
                count = 0
            i = i + 1
        if len(times) > 0:
            capacityA, capacityB = GetCapacity.getCapacity(trashCanA, 0, times[len(times) - 1], trashCanB, 0, times[len(times) - 1])  # 获取容量
        f1.close()
        f2.close()
    timeA = []
    timeB = []
    valueA = []
    valueB = []
    for capacity in capacityA:  # 将容量转化为对应数组，方便传输
        timeA.append(capacity[1])
        valueA.append(capacity[0])
    for capacity in capacityB:  # 将容量转化为对应数组，方便传输
        timeB.append(capacity[1])
        valueB.append(capacity[0])
    return HttpResponse(json.dumps({  # http返回给ajax，用于曲线图描点
        "timeA": json.dumps(timeA),
        "valueA": json.dumps(valueA),
        "timeB": json.dumps(timeB),
        "valueB": json.dumps(valueB)
    }))


def delFile(filePath):  # 清空缓存
    ls = os.listdir(filePath)
    print("Cleaning Cache")
    for i in ls:
        c_path = os.path.join(filePath, i)
        if os.path.isdir(c_path):
            delFile(c_path)
        else:
            os.remove(c_path)


def changeVideoFps(videoPath):
    resultVideoPath = f'result.avi'
    # videoCapture = cv2.VideoCapture(videoPath)
    # fps = videoCapture.get(cv2.CAP_PROP_FPS)
    # if fps != 30:
    #     frameSize = (int(videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    #     # 这里的VideoWriter_fourcc需要多测试，如果编码器不对则会提示报错，根据报错信息修改编码器即可
    #     videoWriter = cv2.VideoWriter(resultVideoPath, cv2.VideoWriter_fourcc('X', 'V', 'I', 'D'), 30, frameSize)
    # clip = VideoFileClip(videoPath)
    # clip.write_videofile(resultVideoPath, fps=30)
    return resultVideoPath


def saveTxt(path, strings, time, trashCanA, trashCanB):  # 保存图片检测结果
    if len(strings) > 0:
        img = cv2.imread(path)
        filePath = path.split(".")[0] + ".txt"  # 获取txt文件名字
        f = open(filePath, 'w')
        for s in strings:
            if s[2][0] > 400:  # 根据x、y坐标区分左右垃圾桶
                trash = "trashCanB"
                trashCanB.append([float(s[1]), s[2], time])
            else:
                trash = "trashCanA"
                trashCanA.append([float(s[1]), s[2], time])
            x, y, w, h = s[2]  # 中心点x，y + w、h
            x1 = int(x - w / 2)
            x2 = int(x + w / 2)
            y1 = int(y - h / 2)
            y2 = int(y + h / 2)
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)  # 对图片进行画框
            cv2.putText(img, trash, (int(x), int(y)), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 0, 0), 2)  # 对图片加字
            f.write("trush   " + str(s[1]) + " ")
            for ss in s[2]:
                f.writelines(str(ss) + "  ")
                # if s[2][0] > 400:
                #     f1.writelines(str(ss) + "  ")
                # else:
                #     f2.writelines(str(ss) + "  ")
            f.writelines('\n')
            # if s[2][0] > 400:
            #     f1.writelines(path)
            #     f1.writelines('\n')
            # else:
            #     f2.writelines(path)
            #     f2.writelines('\n')
        cv2.imwrite(path, img)  # 将框与文字重写入图片
        return True
    else:
        return False


def getImgsPath(videoPath):  # 视频提取帧
    paths = []
    times = []
    # filePath = os.path.dirname(__file__)  # 获取工程运行时路径
    # filePath = filePath.replace("\\", '/')
    delFile(cachePath + '/videoCache')  # 清空缓存
    cap = cv2.VideoCapture(videoPath)  # 获取视频流对象
    fps = cap.get(cv2.CAP_PROP_FPS)  # 获取fps
    per_count = fps // 10
    print("Frames per second using video.get(cv2.CAP_PROP_FPS) : {0}".format(fps))
    success = True
    frame_count = 0
    while success:  # 循环读取图片
        success, frame = cap.read()
        if success and frame is not None and frame_count % per_count == 0:  # 每3帧取一帧图片保存下来，可以自己修改
            milliseconds = cap.get(cv2.CAP_PROP_POS_MSEC)  # 获取当前图片在视频中的时间
            times.append(milliseconds)
            seconds = milliseconds // 1000
            milliseconds = milliseconds % 1000
            minutes = 0
            hours = 0
            if seconds >= 60:
                minutes = seconds // 60
                seconds = seconds % 60
            if minutes >= 60:
                hours = minutes // 60
                minutes = minutes % 60
            ss = str(int(hours)) + "-" + str(int(minutes)) + "-" + str(int(seconds)) + "-" + str(
                int(milliseconds))  # 将时间写成字符串，用于命名
            cv2.imwrite(cachePath + '/videoCache/%s.jpg' % ss, frame)  # 保存为图片
            paths.append(cachePath + '/videoCache/%s.jpg' % ss)  # 添加路径
        frame_count = frame_count + 1
    cap.release()
    return paths, times


def base64_to_img(str):  # 将base64码转换成图片
    data = str.split(',')[1]
    image_data = base64.b64decode(data)
    # filePath = os.path.dirname(__file__)  # 获取当前工程运行路径
    # filePath = filePath.replace("\\", '/')
    curtime = datetime.datetime.now()  # 获取当前时间
    with open(cachePath + '/cameraCache/%s.png' % (
            curtime.strftime('%Y-%m-%d %H:%M:%S.%f')),
              'wb+') as f:  # 写入图片
        f.write(image_data)
    return cachePath + '/cameraCache/%s.png' % (
            curtime.strftime('%Y-%m-%d %H:%M:%S.%f')), curtime  # 返回时间与图片路径


# 摄像头输入
cameraTrashCanA = []
cameraTrashCanB = []
cameraImgPaths = []
cameraCurTimes = []
cameraBeginTimeA = 0
cameraBeginTimeB = 0

# 模拟测试摄像头输入
imagePaths, curTimes = getImgsPath('/home/lxp/桌面/video/标准.mp4')  # 视频处理为图片
cameraBeginTime = 0  # 计时器
imgCount = 0  # 计数器
# 模拟测试摄像头输入


def camera_detect(request):  # 摄像头输入图片
    global cameraCurTimes, cameraImgPaths, imgCount, imagePaths  # 申明调用全局变量
    if request.method == "POST":
        photoPath = request.POST.get('Path')
        imgPath, curTime = base64_to_img(photoPath)  # 获取图片信息
        # cameraImgPaths.append(imgPath)  # 存储图片
        # cameraCurTimes.append(curTime)  # 存储对应时间
        if imgCount < len(imagePaths):  # 模拟输入
            cameraImgPaths.append(imagePaths[imgCount])
            cameraCurTimes.append(curTimes[imgCount])
            imgCount = imgCount + 1
    return HttpResponse(1)


def getCameraCapacity(request):
    cameraCapacityAIndex = 0
    cameraCapacityBIndex = 0
    cameraCapacityA = []
    cameraCapacityB = []

    global cameraTrashCanA, cameraTrashCanB, cameraCurTimes, cameraImgPaths, cameraBeginTimeA, cameraBeginTimeB  # 申明调用全局变量
    if len(cameraImgPaths) >= 100:  # 当图片超过100张时
        count = 0
        i = 0
        while i < len(cameraImgPaths):  # 循环
            if not saveTxt(cameraImgPaths[i], darknet.detect(net, meta, cameraImgPaths[i]), cameraCurTimes[i],
                           cameraTrashCanA, cameraTrashCanB):  # 判断是否检测到图片
                count = count + 1
                begin = False
            else:
                begin = True
                count = 0
            if (not begin) and count > 5:  # 连续5次美检测到， 进行跳跃式检测
                index = i
                while index + 10 < len(cameraImgPaths) and len(
                        darknet.detect(net, meta, cameraImgPaths[index + 10])) < 1:  # 每隔一秒判断一次,寻找下一个起始点
                    index = index + 10
                i = index
                count = 0
            i = i + 1
        cameraCapacityA, cameraCapacityB = GetCapacity.getCapacity(cameraTrashCanA, cameraBeginTimeA,
                                                                   cameraCurTimes[len(cameraCurTimes) - 1],
                                                                   cameraTrashCanB, cameraBeginTimeB,
                                                                   cameraCurTimes[len(cameraCurTimes) - 1])  # 获取容量
        cameraTrashCanAIndex, cameraCapacityAIndex, cameraBeginTimeA = findSplitPoint(cameraCapacityA,
                                                                                      cameraTrashCanA)  # 获取关键下标以及下次计算开始时间
        cameraTrashCanBIndex, cameraCapacityBIndex, cameraBeginTimeB = findSplitPoint(cameraCapacityB,
                                                                                      cameraTrashCanB)  # 获取关键下标以及下次计算开始时间
        cameraImgPaths.clear()  # 清空缓存 防止重复计算
        cameraCurTimes.clear()  # 清空缓存 防止重复计算
        saveCameraTrashCan(cameraTrashCanAIndex, cameraTrashCanA)  # 取舍垃圾桶信息
        saveCameraTrashCan(cameraTrashCanBIndex, cameraTrashCanB)  # 取舍垃圾桶信息
    timeA = []
    timeB = []
    valueA = []
    valueB = []
    for i in range(cameraCapacityAIndex):  # 根据下标选择性输出容量信息
        timeA.append(cameraCapacityA[i][1])
        valueA.append(cameraCapacityA[i][0])
    for i in range(cameraCapacityBIndex):  # 根据下标选择性输出容量信息
        timeB.append(cameraCapacityB[i][1])
        valueB.append(cameraCapacityB[i][0])
    return HttpResponse(json.dumps({  # http返回给ajax，用于曲线图描点
        "timeA": json.dumps(timeA),
        "valueA": json.dumps(valueA),
        "timeB": json.dumps(timeB),
        "valueB": json.dumps(valueB)
    }))


def saveCameraTrashCan(index, trashCan):  # 取舍垃圾信息
    del trashCan[0:index]


def findSplitPoint(capacitious, trashCan):  # 查找转折点并返回关键信息  转折点处垃圾桶信息下标、 转折点处容量信息下标、 转折点后的开始时间
    count = 0
    splitTime = 0
    splitCapacityIndex = 0
    if len(capacitious) > 0:
        for i in range(len(capacitious) - 1):  # 循环查找
            if capacitious[i][0] != capacitious[i + 1][0]:  # 如果出现转折点
                count = count + 1
                if count == 1:
                    if capacitious[i + 1][1] - capacitious[i][1] > 1000:  # 记录转折点时间，若i+1时间 - i时间大于1s 取前者-1s作为开始时间
                        splitTime = capacitious[i + 1][1] - 1000
                    else:
                        splitTime = capacitious[i][1]
                    splitCapacityIndex = i
    if count == 0:  # 分情况输出转折点信息
        return len(trashCan), len(capacitious), capacitious[len(capacitious) - 1][1]
    else:
        return findTrashCanIndex(splitTime, trashCan), splitCapacityIndex + 1, splitTime


def findTrashCanIndex(time, trashCan):  # 根据时间寻找对应垃圾桶下标  用于后面的垃圾桶信息的取舍
    index = 0
    for i in range(len(trashCan) - 2):  # 循环查找
        if trashCan[i][2] <= time <= trashCan[i + 1][2] or trashCan[i + 1][2] <= time <= trashCan[i][2]:  # 转折点
            if time == trashCan[i + 1][2]:
                index = i + 2
            else:
                index = i + 1
            break
    return index  # 返回下标


def saveCachePath(path):
    global cachePath
    cachePath = path
    videoCachePath = cachePath + '/videoCache'
    cameraCachePath = cachePath + '/cameraCache'
    if os.path.exists(videoCachePath):
        data = 1
        # delFile(videoCachePath)
        # delFile(cameraCachePath)
    else:
        os.makedirs(videoCachePath)
        os.makedirs(cameraCachePath)
