# -*- coding: utf-8 -*-

__author__ = "zyqzyq"
__time__ = '2018/3/29 9:57'

from math import radians, cos, sin, asin, sqrt


# 计算两点间距离-km
def geodistance(lng1, lat1, lng2, lat2):
    lng1, lat1, lng2, lat2 = map(radians, [lng1, lat1, lng2, lat2])
    dlon = lng2 - lng1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    dis = 2 * asin(sqrt(a)) * 6371
    return dis


if __name__ == '__main__':
    print geodistance(117.17, 31.52, 117.17, 31.52)
