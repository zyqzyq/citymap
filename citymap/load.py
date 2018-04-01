# -*- coding: UTF-8 -*-
import MySQLdb
import geohash
from math import radians, cos, sin, asin, sqrt
import redis


def geo_distance(lng1, lat1, lng2, lat2):
    lng1, lat1, lng2, lat2 = map(radians, [lng1, lat1, lng2, lat2])
    dlon = lng2 - lng1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    dis = 2 * asin(sqrt(a)) * 6371
    return dis


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


def load_redis():
    # 打开数据库连接
    pool = redis.ConnectionPool(host='127.0.0.1', port=6379)
    conn = redis.Redis(connection_pool=pool)
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
        for i, result in enumerate(results):
            # data = {"name": result[1], "value": [result[2], result[3]]}
            conn.hset(name=result[1], key="east", value=result[2])
            conn.hset(name=result[1], key="north", value=result[3])
            conn.hset(name=result[1], key="id", value=i)
            for j, other_result in enumerate(results):
                # if i == j :
                # print "dist:",geo_distance(result[2], result[3], other_result[2], other_result[3])
                conn.hset(name=result[1], key=str(j),
                          value=geo_distance(result[2], result[3], other_result[2], other_result[3]))
            # self.conn.set(result[1], [result[2], result[3]])
        # print self.data
    except:
        # 发生错误时回滚
        print  "Error: unable to fecth data"
    # 关闭数据库连接
    db.close()


if __name__ == '__main__':
    create_table()
    insert_data()
    load_redis()
