from django.contrib import admin
from django.urls import path
import cv2
import os
import time
import base64
import threading
import json
from django.contrib import messages
from django.shortcuts import render
from django.shortcuts import HttpResponse  # 导入该模块
from darknet import darknet
from MyCode import GetCapacity


# net, meta = darknet.loadModle()


def video_detect(request):
    capacityA = []
    capacityB = []
    if request.method == "POST":
        print("begin")
        videoPath = request.FILES['video'].temporary_file_path()
        # f1 = open('data.txt', "w")
        # f2 = open('data2.txt', "w")
        imagesPaths, times, fps = getImgsPath(videoPath)
        trashA = []
        trashB = []
        count = 0
        begin = False
        for i in range(len(imagesPaths)):
            getCameraCapacitious(imagesPaths[i], times[i])
        # f1.close()
        # f2.close()
    timeA = []
    timeB = []
    valueA = []
    valueB = []
    for capacity in capacityA:
        timeA.append(capacity[1])
        valueA.append(capacity[0])
    for capacity in capacityB:
        timeB.append(capacity[1])
        valueB.append(capacity[0])
    return HttpResponse(json.dumps({
        "timeA": json.dumps(timeA),
        "valueA": json.dumps(valueA),
        "timeB": json.dumps(timeB),
        "valueB": json.dumps(valueB)
    }))


def saveTxt(path, strings, time, trashA, trashB):
    if len(strings) > 0:
        img = cv2.imread(path)
        filePath = path.split(".")[0] + ".txt"
        f = open(filePath, 'w')
        for s in strings:
            if s[2][0] > 400:
                trash = "trashB"
                trashB.append([float(s[1]), s[2], time])
            else:
                trash = "trashA"
                trashA.append([float(s[1]), s[2], time])
            x, y, w, h = s[2]  # 中心点x，y + w、h
            x1 = int(x - w / 2)
            x2 = int(x + w / 2)
            y1 = int(y - h / 2)
            y2 = int(y + h / 2)
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(img, trash, (int(x), int(y)), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 0, 0), 2)
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
        cv2.imwrite(path, img)
        return True
    else:
        return False


def getImgsPath(videoPath):
    paths = []
    times = []
    filePath = os.path.dirname(__file__)
    filePath = filePath.replace("\\", '/')
    cap = cv2.VideoCapture(videoPath)
    fps = cap.get(cv2.CAP_PROP_FPS)
    per_count = fps / 10
    print("Frames per second using video.get(cv2.CAP_PROP_FPS) : {0}".format(fps))
    success = True
    frame_count = 0
    while success:
        success, frame = cap.read()
        if success and frame is not None and frame_count % per_count == 0:  # 每3帧取一帧图片保存下来，可以自己修改
            milliseconds = cap.get(cv2.CAP_PROP_POS_MSEC)
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
            ss = str(int(hours)) + "-" + str(int(minutes)) + "-" + str(int(seconds)) + "-" + str(int(milliseconds))
            cv2.imwrite(filePath + '/MyCache/videoCache/%s.jpg' % ss, frame)
            paths.append(filePath + '/MyCache/videoCache/%s.jpg' % ss)
        frame_count = frame_count + 1
    cap.release()
    return paths, times, fps


def base64_to_img(str):
    data = str.split(',')[1]
    image_data = base64.b64decode(data)
    filePath = os.path.dirname(__file__)
    filePath = filePath.replace("\\", '/')
    curtime = time.localtime(time.time())
    with open(filePath + '/MyCache/cameraCache/%s.jpg' % (
            time.strftime('%Y-%m-%d-%H-%M-%S', curtime)),
              'wb+') as f:
        f.write(image_data)
    return filePath + '/MyCache/cameraCache/%s.jpg' % (time.strftime('%Y-%m-%d-%H-%M-%S', curtime)), curtime


# 摄像头输入
cameraTrashCanA = []
cameraTrashCanB = []
cameraImgPaths = []
cameraCurTimes = []
cameraBeginTimeA = 0
cameraBeginTimeB = 0

def camera_detect(request):
    cameraCapacityA = []
    cameraCapacityB = []
    timeA = []
    timeB = []
    valueA = []
    valueB = []
    cameraCapacityAIndex = 0
    cameraCapacityBIndex = 0
    if request.method == "POST":
        photoPath = request.POST.get('Path')
        imgPath, curTime = base64_to_img(photoPath)
        cameraImgPaths.append(imgPath)
        cameraCurTimes.append(curTime)
        if len(cameraImgPaths) > 70:
            for i in range(len(cameraImgPaths)):
                count = 0
                begin = False
                if saveTxt(cameraImgPaths[i], darknet.detect(net, meta, cameraImgPaths[i]), cameraCurTimes[i],
                           cameraTrashCanA, cameraTrashCanB):
                    count = count + 1
                else:
                    begin = True
                    count = 0
                if begin and count > 5:
                    index = i
                    while len(darknet.detect(net, meta, cameraImgPaths[i])) < 1:  # 每隔一秒判断一次,寻找下一个起始点
                        index = index + 10
                    i = index
                    count = 0
                    begin = False
            print(cameraTrashCanA, cameraTrashCanB, " in")
            cameraCapacityA, cameraCapacityB = GetCapacity.getCapacity(cameraTrashCanA, cameraTrashCanB)
            cameraTrashCanAIndex, cameraCapacityAIndex = findSplitPoint(cameraCapacityA, cameraTrashCanA)
            cameraCapacityBIndex, cameraCapacityBIndex = findSplitPoint(cameraCapacityB, cameraTrashCanB)
            saveCameraTrashCan(cameraCapacityAIndex, cameraTrashCanA)
            saveCameraTrashCan(cameraCapacityBIndex, cameraTrashCanB)

    for i in range(cameraCapacityAIndex):
        timeA.append(cameraCapacityA[i][1])
        valueA.append(cameraCapacityA[i][0])
    for i in range(cameraCapacityBIndex):
        timeB.append(cameraCapacityB[i][1])
        valueB.append(cameraCapacityB[i][0])
    return HttpResponse(json.dumps({
        "timeA": json.dumps(timeA),
        "valueA": json.dumps(valueA),
        "timeB": json.dumps(timeB),
        "valueB": json.dumps(valueB)
    }))


def saveCameraTrashCan(index, trashCan):
    del trashCan[0:index]


def findSplitPoint(capacitious, trashCan):
    count = 0
    splitTime = 0
    splitCapacityIndex = 0
    if len(capacitious) > 0:
        for i in range(len(capacitious) - 1):
            if capacitious[i][0] != capacitious[i + 1][0]:
                count = count + 1
                if count == 1:
                    if capacitious[i + 1][1] - capacitious[i][1] > 1000:
                        splitTime = capacitious[i + 1][1] - 1000
                    else:
                        splitTime = capacitious[i][1]
                    splitCapacityIndex = i
    if count == 0:
        return len(trashCan), len(capacitious), capacitious[len(capacitious) - 1][1]
    else:
        return findTrashCanIndex(splitTime, trashCan), splitCapacityIndex + 1, splitTime


def findTrashCanIndex(time, trashCan):
    index = 0
    for i in range(len(trashCan) - 2):
        if trashCan[i][2] <= time <= trashCan[i + 1][2] or trashCan[i + 1][2] <= time <= trashCan[i][2]:
            if time == trashCan[i + 1][2]:
                index = i + 2
            else:
                index = i + 1
            break
    return index


def getCameraCapacitious(imgPath, curTime, cameraCurTime=None):
    cameraCapacityAIndex = 0
    cameraCapacityBIndex = 0
    cameraCapacityA = []
    cameraCapacityB = []
    global cameraTrashCanA, cameraTrashCanB, cameraCurTimes, cameraImgPaths, cameraBeginTimeA, cameraBeginTimeB  # 申明调用全局变量
    cameraImgPaths.append(imgPath)
    cameraCurTimes.append(curTime)
    if len(cameraImgPaths) > 100:
        count = 0
        i = 0
        while i < len(cameraImgPaths):
            if not saveTxt(cameraImgPaths[i], darknet.detect(net, meta, cameraImgPaths[i]), cameraCurTimes[i], cameraTrashCanA, cameraTrashCanB):
                count = count + 1
                begin = False
            else:
                begin = True
                count = 0
            if (not begin) and count > 5:
                index = i
                while index + 10 < len(cameraImgPaths) and len(
                        darknet.detect(net, meta, cameraImgPaths[index + 10])) < 1:  # 每隔一秒判断一次,寻找下一个起始点
                    index = index + 10
                i = index
                count = 0
            i = i + 1
        cameraCapacityA, cameraCapacityB = GetCapacity.getCapacity(cameraTrashCanA, cameraBeginTimeA, curTime, cameraTrashCanB, cameraBeginTimeB, curTime)

        cameraTrashCanAIndex, cameraCapacityAIndex, cameraBeginTimeA = findSplitPoint(cameraCapacityA, cameraTrashCanA)
        cameraTrashCanBIndex, cameraCapacityBIndex, cameraBeginTimeB = findSplitPoint(cameraCapacityB, cameraTrashCanB)
        cameraImgPaths.clear()
        cameraCurTimes.clear()
        saveCameraTrashCan(cameraTrashCanAIndex, cameraTrashCanA)
        saveCameraTrashCan(cameraTrashCanBIndex, cameraTrashCanB)
        
    for i in range(cameraCapacityBIndex):
        print(cameraCapacityB[i][0], cameraCapacityB[i][1])
