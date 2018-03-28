#!/usr/bin/python
# -*- coding: UTF-8 -*-

import MySQLdb
import redis

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
        sql = "INSERT INTO CITYLIST(ID, CITY_NAME, \
               EAST, NORTH) \
               VALUES (%d ,'%s', '%f', '%f')" % \
              (i, sheet.cell(i, 1).value.encode("utf-8"), sheet.cell(i, 3).value, sheet.cell(i, 2).value)
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
            data = [result[1],[result[2],result[3]]]
            data_json["city"].append(data)
        # print data_json
    except:
        # 发生错误时回滚
        print "Error: unable to fecth data"

    # 关闭数据库连接
    db.close()
    return data_json

def test_redis(data):
    pool = redis.ConnectionPool(host='127.0.0.1',password="123456", port=6379)
    r = redis.Redis(connection_pool=pool)
    for i in data["city"]:
        print i
        print i[0],i[1]
        r.set(i[0].encode('utf-8'),i[1])



if __name__ == '__main__':
    # create_table()  # 新建表格
    # insert_data()     # 插入数据
    data = search_all()
    # print data
    # test_redis(data)