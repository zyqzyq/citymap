# -*- coding: utf-8 -*-

__author__ = "zyqzyq"
__time__ = '2018/3/29 10:25'
import geohash

if __name__ == '__main__':
    print geohash.encode(39.92324, 116.3906, 4)
    print geohash.expand('wx4g')
    print geohash.decode('wx4g')
