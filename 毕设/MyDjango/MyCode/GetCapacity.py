import numpy as np
from scipy.optimize import leastsq


def calAvg(array):  # 平均数
    sum = 0
    for a in array:
        sum = sum + a[2]
    return sum / len(array)


def calVariance(array, avg):  # 标准差
    sum = 0
    for a in array:
        sum = pow((a[2] - avg), 2) + sum
    sum = sum / len(array)
    return pow(sum, 0.5)


def getCapacity(trashCanA, beginTimeA, endTimeA, trashCanB, beginTimeB, endTimeB):  # 计算容量 维护一个开始结束时间 确保容量计算都在该时间段内
    print("Calculating Capacity !!!")
    # print(len(trashCanA))
    # print("trashA")
    capacityA = calCapacity(trashCanA, beginTimeA, endTimeA)  # 计算容量
    # print(len(trashCanB))
    # print("trashB")
    capacityB = calCapacity(trashCanB, beginTimeB, endTimeB)  # 计算容量
    return capacityA, capacityB


def calCapacity(trashCan, beginTime, endTime):  # 计算容量
    capacity = 0
    capacious = []
    isTrash = False
    isFirst = True
    beginIndex = 0
    endIndex = 0
    if len(trashCan) > 0:
        for i in range(len(trashCan)):  # 循环
            if beginTime <= trashCan[i][2] <= endTime:  # 判断是否在时间段内
                if i == 0 and trashCan[i][2] - beginTime >= 2000:  # 判断前部分是否需要补充坐标
                    supplyCapacity(beginTime, trashCan[i][2], capacious)  # 补充头部坐标时间
                count, properties, points, times = getFirstSecondInfo(i, trashCan)
                if (not isTrash) and (float(count) / float(10) * 100 >= 80):  # 判断是否开始， 连续的点应符合百分比才算开始
                    isTrash = True
                if isTrash:  # 正在翻桶
                    avgWeight = calAvg(points)  # 获取平均宽
                    varianceWeight = calVariance(points, avgWeight)  # 计算标准差
                    if isFirst and varianceWeight < 100:  # 根据标准差判断离散程度
                        print("avgWeight", avgWeight)
                        isFirst = False
                        beginIndex = i
                        supplyCapacity(trashCan[endIndex][2], trashCan[beginIndex][2], capacious)  # 填充坐标为【0， time】
                        if 155 < avgWeight <= 175.0:  # 第一层 根据宽不同判断容量大小
                            capacity = 240
                        else:
                            if 140.0 < avgWeight <= 155.0:
                                capacity = 120
                            else:
                                if 130.0 < avgWeight <= 140.0:
                                    capacity = 100
                                else:
                                    if 120.0 < avgWeight <= 130.0:
                                        capacity = 80
                if (isTrash and i < len(trashCan) - 1 and trashCan[i + 1][2] - trashCan[i][2] > 1000) or (
                        isTrash and i + 1 >= len(trashCan)):  # 两张图间隔超过1秒就断定翻桶结束
                    isTrash = False
                    isFirst = True
                    endIndex = i
                    maxHeight = getMaxHeight(trashCan, beginIndex, i)  # 获取抛物线的最高点
                    print("height", maxHeight)
                    if 350.0 < maxHeight < 450.0:  # 第二层 根据最高的判断容量大小
                        capacity = 240
                    else:
                        if 290.0 < maxHeight <= 350.0:
                            capacity = 120
                        else:
                            if 240.0 < maxHeight <= 290.0:
                                capacity = 100
                    saveCapacity(capacity, trashCan, beginIndex, endIndex, capacious)  # 填充坐标信息
                if i == len(trashCan) - 1 and endTime - trashCan[i][2] >= 2000:  # 补充尾部坐标时间
                    supplyCapacity(trashCan[i][2], endTime, capacious)
    else:
        if endTime - beginTime >= 2000:  # 时间段内无垃圾桶信息 直接补充坐标
            supplyCapacity(beginTime, endTime, capacious)
    return capacious


def supplyCapacity(beginTime, endTime, capacious):  # 填充坐标
    timeSpan = 1000
    # for i in range(beginIndex, endIndex):
    #     if trashCan[i][2] - beginTime >= timeSpan:
    #         beginTime = trashCan[i][2]
    #         print(0, trashCan[i][2])
    #         capacious.append([0, beginTime])
    while beginTime + timeSpan < endTime:  # 判断是否超时
        capacious.append([0, beginTime])
        if beginTime + 2000 < endTime:  # 判断是否可以2s一填或1s一填
            beginTime = beginTime + 2000
        else:
            beginTime = beginTime + timeSpan


def getFirstSecondInfo(i, trashCan):  # 获取第一秒内垃圾桶信息
    properties = []
    points = []
    times = []
    timeBegin = trashCan[i][2]
    timeSpan = 1000
    count = 0
    while count < 10 and i + count < len(trashCan) and trashCan[i + count][2] - timeBegin <= timeSpan:  # 循环查找
        property = trashCan[i + count][0]  # 填充对应信息
        point = trashCan[i + count][1]
        time = trashCan[i + count][2]
        properties.append(property)
        points.append(point)
        times.append(time)
        count = count + 1
    return count, properties, points, times  # 返回1s内信息


def func(params, x):  # 二次函数的标准形式
    a, b, c = params
    return a * x * x + b * x + c


def error(params, x, y):  # 误差函数，即拟合曲线所求的值与实际值的差
    return func(params, x) - y


def solvePara(X, Y):  # 对参数求解
    p0 = [10, 10, 10]
    Para = leastsq(error, p0, args=(X, Y))
    return Para


def getMaxHeight(trashCan, begin, end):  # 获取最高点
    heights = []
    times = []
    timeBegin = trashCan[begin][2]
    for i in range(begin, end):  # 循环
        heights.append(trashCan[i][1][3])  # x, y, w, h  填充为y
        times.append((trashCan[i][2] - timeBegin + 1) // 100)  # 填充为x
    A, B, C = solvePara(np.array(times), np.array(heights))[0]  # 抛物线拟合 得到A、B、C
    return (4 * A * C - pow(B, 2)) / (4 * A)  # 返回最高点


def saveCapacity(value, trashCan, begin, end, capacious):  # 保存容量信息
    timeSpan = 1000
    beginTime = trashCan[begin][2]
    capacious.append([value, trashCan[begin][2]])
    for i in range(begin, end):  # 下标循环
        if trashCan[i][2] - beginTime >= timeSpan:  # 一秒一填
            beginTime = trashCan[i][2]
            # print(value, trashCan[i][2])
            capacious.append([value, trashCan[i][2]])
