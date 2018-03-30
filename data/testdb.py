#!/usr/bin/python
# -*- coding: UTF-8 -*-

import MySQLdb
import geohash
import redis
from math import radians, cos, sin, asin, sqrt
from operator import itemgetter

def create_table():
    # 打开数据库连接
    db = MySQLdb.connect("localhost", "root", "root", "citydb")

    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    # 如果数据表已经存在使用 execute() 方法删除表。
    cursor.execute("DROP TABLE IF EXISTS CITYLIST")

    # 创建数据表SQL语句
    sql = """CREATE TABLE `citydb`.`CITYLIST` (
              `ID` INT NOT NULL,
              `CITY_NAME` CHAR(20) NULL,
              `EAST` FLOAT NULL,
              `NORTH` FLOAT NULL,
              `GEOHASH` CHAR(20) NULL,
              PRIMARY KEY (`ID`));"""

    cursor.execute(sql)

    # 关闭数据库连接
    db.close()


def insert_data():
    import xlrd
    # 打开数据库连接
    db = MySQLdb.connect("localhost", "root", "root", "citydb")

    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    ExcelFile = xlrd.open_workbook("citylist.xls")
    print ExcelFile.sheet_names()
    sheet = ExcelFile.sheet_by_index(0)
    print sheet.name, sheet.nrows, sheet.ncols
    for i in range(1, sheet.nrows):
        # data = {"name": sheet.cell(i, 1).value, "value": [sheet.cell(i, 3).value, sheet.cell(i, 2).value]}
        # SQL 插入语句
        east_longitude = sheet.cell(i, 3).value
        north_latitude = sheet.cell(i, 2).value
        geohash_value = geohash.encode(north_latitude, east_longitude, 6)
        sql = "INSERT INTO CITYLIST(ID, CITY_NAME, \
               EAST, NORTH, GEOHASH) \
               VALUES (%d ,'%s', '%f', '%f','%s')" % \
              (i, sheet.cell(i, 1).value.encode("utf-8"), east_longitude, north_latitude, geohash_value)
        try:
            # 执行sql语句
            cursor.execute(sql)
            # 提交到数据库执行
            db.commit()
        except:
            # 发生错误时回滚
            db.rollback()
            print "error "

    # 关闭数据库连接
    db.close()


def search_all():
    # 打开数据库连接
    data_json = {"city": []}
    db = MySQLdb.connect("localhost", "root", "root", "citydb")

    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    # SQL 插入语句
    sql = "SELECT * FROM CITYLIST"
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        results = cursor.fetchall()
        for result in results:
            data = [result[1], [result[2], result[3]]]
            data_json["city"].append(data)
        # print data_json
    except:
        # 发生错误时回滚
        print "Error: unable to fecth data"

    # 关闭数据库连接
    db.close()
    return data_json


def test_redis(data):
    pool = redis.ConnectionPool(host='127.0.0.1', port=6379)

    r = redis.Redis(connection_pool=pool)
    keys = r.keys()
    r.delete(*keys)
    for i in data["city"]:
        r.hset(name=i[0], key="1", value=i[1][0])
        r.hset(name=i[0], key="2", value=i[1][1])
    city_list = []
    keys = r.keys()
    print type(keys)
    print keys
    for key in keys:
        value = r.hgetall(key)
        city_list.append({"name": key, "value": [float(value["1"]), float(value["2"])]})
    print city_list
    keys = r.keys()
    r.delete(*keys)


def search_geohash(east_longitude, north_latitude, bits=6):
    # 打开数据库连接
    data = []
    geohash_source = geohash.encode(north_latitude, east_longitude, bits)
    # print geohash_source
    geohash_value_list = geohash.expand(geohash_source)
    # geohash_value_list.append(geohash_source)
    db = MySQLdb.connect("localhost", "root", "root", "citydb")
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    # SQL 插入语句
    for geohash_value in geohash_value_list:
        sql = "SELECT * FROM CITYLIST WHERE GEOHASH LIKE '{}%'".format(geohash_value)
        try:
            # 执行sql语句
            cursor.execute(sql)
            # 提交到数据库执行
            results = cursor.fetchall()
            for result in results:
                data.append(result)
            # print data_json
        except:
            # 发生错误时回滚
            print "Error: unable to fecth data"
        # 关闭数据库连接
    db.close()
    if len(data) < 3:
        return search_geohash(east_longitude, north_latitude, bits - 1)
    else:
        return data


def search_nearby_city(east_longitude, north_latitude):
    city_distance_list = []
    nearby_city_list = search_geohash(east_longitude, north_latitude)
    # print nearby_city_list
    for city in nearby_city_list:
        city_distance = (city[1], geo_distance(city[2], city[3], east_longitude, north_latitude))
        city_distance_list.append(city_distance)
    # print city_distance_list
    # print sorted(city_distance_list, key=itemgetter(1))[:3]
    for city in sorted(city_distance_list, key=itemgetter(1))[:3]:
        print city[0]


def geo_distance(lng1, lat1, lng2, lat2):
    lng1, lat1, lng2, lat2 = map(radians, [lng1, lat1, lng2, lat2])
    dlon = lng2 - lng1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    dis = 2 * asin(sqrt(a)) * 6371
    return dis


if __name__ == '__main__':
    create_table()  # 新建表格
    insert_data()     # 插入数据
    # data = search_all()
    # print data
    # test_redis(data)
    # search_geohash()
    # search_nearby_city(116.28, 31.44)
