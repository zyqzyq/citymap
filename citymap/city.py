# -*- coding: utf-8 -*-
import redis

__author__ = "zyqzyq"
__time__ = '2018/3/27 11:26'

import falcon
import MySQLdb
import json
import geohash
from math import radians, cos, sin, asin, sqrt
from operator import itemgetter


class CityResource(object):

    def __init__(self):
        self.pool = redis.ConnectionPool(host='127.0.0.1', port=6379)
        self.conn = redis.Redis(connection_pool=self.pool)
        self.init_redis()

    def process_response(self, req, resp, resource, req_succeeded):
        resp.set_header('Access-Control-Allow-Origin', '*')

        if (req_succeeded
                and req.method == 'OPTIONS'
                and req.get_header('Access-Control-Request-Method')
        ):
            # NOTE(kgriffs): This is a CORS preflight request. Patch the
            #   response accordingly.

            allow = resp.get_header('Allow')
            resp.delete_header('Allow')

            allow_headers = req.get_header(
                'Access-Control-Request-Headers',
                default='*'
            )

            resp.set_headers((
                ('Access-Control-Allow-Methods', allow),
                ('Access-Control-Allow-Headers', allow_headers),
                ('Access-Control-Max-Age', '86400'),  # 24 hours
            ))

    def on_get(self, req, resp):
        resp.set_header('Access-Control-Allow-Origin', '*')  # 避免跨域问题
        page = req.get_param_as_int("page") or 1
        num = req.get_param_as_int("num") or 20
        city_list, count, next_page_url = self.get_data(page, num)
        # print len(self.data["city"])
        dict_data = {
            "city": city_list,
            "count": count,
            "next_page_url": next_page_url,
        }
        resp.data = json.dumps(dict_data)
        resp.status = falcon.HTTP_200

    def get_data(self, page, num):
        city_list = []
        keys = self.conn.keys()
        if page * num < len(keys):
            count = num
            next_page_url = "http://localhost:8000/city?page={}&num={}".format(page + 1, num)
            for key in keys[(page - 1) * num:page * num]:
                value = self.conn.hgetall(key)
                city_list.append({"name": key, "value": [float(value["1"]), float(value["2"])]})
        elif (page - 1) * num < len(keys) < page * num:
            count = page * num - len(keys)
            next_page_url = None
            for key in keys[(page - 1) * num:]:
                value = self.conn.hgetall(key)
                city_list.append({"name": key, "value": [float(value["1"]), float(value["2"])]})
        else:
            count = None
            next_page_url = None
        return city_list, count, next_page_url

    def init_redis(self):
        # 打开数据库连接
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
                # data = {"name": result[1], "value": [result[2], result[3]]}
                self.conn.hset(name=result[1], key="1", value=result[2])
                self.conn.hset(name=result[1], key="2", value=result[3])
                # self.conn.set(result[1], [result[2], result[3]])
            # print self.data
        except:
            # 发生错误时回滚
            print  "Error: unable to fecth data"
        # 关闭数据库连接
        db.close()


class SearchResource(object):

    def on_get(self, req, resp, east_longitude, north_latitude):
        # print req, resp, east_longitude, north_latitude
        resp.set_header('Access-Control-Allow-Origin', '*')  # 避免跨域问题
        rec = 4
        info = None
        nearby_city_list = []
        east_longitude, north_latitude = float(east_longitude), float(north_latitude)
        if 4 < north_latitude < 53 and 73 < east_longitude < 135:
            rec = 0
            nearby_city_list = self.search_nearby_city(east_longitude, north_latitude)
        else:
            info = "error: 经纬度超出范围，请输入北纬4~53度，东经73~135度的参数。"
        dict_data = {
            "rec": rec,
            "city_list": nearby_city_list,
            "info": info,
        }
        resp.data = json.dumps(dict_data)
        resp.status = falcon.HTTP_200

    def search_geohash(self, east_longitude, north_latitude, bits=6):
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
            return self.search_geohash(east_longitude, north_latitude, bits - 1)
        else:
            return data

    def search_nearby_city(self, east_longitude, north_latitude):
        city_distance_list = []
        city_name_list = []
        nearby_city_list = self.search_geohash(east_longitude, north_latitude)
        # print nearby_city_list
        for city in nearby_city_list:
            city_distance = (city[1], self.geo_distance(city[2], city[3], east_longitude, north_latitude))
            city_distance_list.append(city_distance)
        # print city_distance_list
        # print sorted(city_distance_list, key=itemgetter(1))[:3]
        for city in sorted(city_distance_list, key=itemgetter(1))[:3]:
            city_name_list.append(city[0])
        return city_name_list

    def geo_distance(self, lng1, lat1, lng2, lat2):
        lng1, lat1, lng2, lat2 = map(radians, [lng1, lat1, lng2, lat2])
        dlon = lng2 - lng1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        dis = 2 * asin(sqrt(a)) * 6371
        return dis
