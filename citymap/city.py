# -*- coding: utf-8 -*-
import redis

__author__ = "zyqzyq"
__time__ = '2018/3/27 11:26'

import falcon
import MySQLdb
import json
import geohash
import numpy as np
from math import radians, cos, sin, asin, sqrt
from operator import itemgetter
import itertools
import copy


def geo_distance(lng1, lat1, lng2, lat2):
    lng1, lat1, lng2, lat2 = map(radians, [lng1, lat1, lng2, lat2])
    dlon = lng2 - lng1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    dis = 2 * asin(sqrt(a)) * 6371
    return dis


def is_float(value):
    if value.count(".") == 1:
        new_value = value.split(".")
        if new_value[0].isdigit() and new_value[1].isdigit():
            return True
        else:
            return False
    elif value.isdigit():
        return True
    else:
        return False


def is_checked(lng, lat):
    if is_float(lat) and is_float(lng):
        lng, lat = float(lng), float(lat)
        if 73 < lng < 135 and 4 < lat < 53:
            return True
    else:
        return False


class CityResource(object):

    def __init__(self):
        self.pool = redis.ConnectionPool(host='127.0.0.1', port=6379)
        self.conn = redis.Redis(connection_pool=self.pool)
        self.host = "localhost"

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
        if 0 < page * num < len(keys):
            count = num
            next_page_url = "http://{}:8000/city?page={}&num={}".format(self.host, page + 1, num)
            for key in keys[(page - 1) * num:page * num]:
                value = self.conn.hgetall(key)
                city_list.append({"name": key, "value": [float(value["east"]), float(value["north"])]})
        elif (page - 1) * num < len(keys) < page * num:
            count = page * num - len(keys)
            next_page_url = None
            for key in keys[(page - 1) * num:]:
                value = self.conn.hgetall(key)
                city_list.append({"name": key, "value": [float(value["east"]), float(value["north"])]})
        else:
            count = None
            next_page_url = None
        return city_list, count, next_page_url


class SearchResource(object):

    def on_get(self, req, resp, east_longitude, north_latitude):
        # print req, resp, east_longitude, north_latitude
        resp.set_header('Access-Control-Allow-Origin', '*')  # 避免跨域问题
        rec = 4
        info = None
        nearby_city_list = []
        # east_longitude, north_latitude = float(east_longitude), float(north_latitude)
        if is_checked(east_longitude, north_latitude):
            rec = 0
            east_longitude, north_latitude = float(east_longitude), float(north_latitude)
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
        data = []
        geohash_source = geohash.encode(north_latitude, east_longitude, bits)
        # print geohash_source
        geohash_value_list = geohash.expand(geohash_source)
        # 打开数据库连接
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
            city_distance = (city[1], geo_distance(city[2], city[3], east_longitude, north_latitude))
            city_distance_list.append(city_distance)
        # print city_distance_list
        # print sorted(city_distance_list, key=itemgetter(1))[:3]
        for city in sorted(city_distance_list, key=itemgetter(1))[:3]:
            city_name_list.append(city[0])
        return city_name_list


class TSPResource(object):

    def __init__(self, conn):
        self.conn = conn
        self.matrix = None
        self.S = []
        self.sum = 0
        self.n = 999
        self.init_matrix()

    def on_get(self, req, resp, start_east, start_north, end_east, end_north):
        resp.set_header('Access-Control-Allow-Origin', '*')
        # start_east, start_north, end_east, end_north = float(start_east), float(start_north), float(end_east), float(
        #     end_north)
        # print start_east, start_north, end_east, end_north
        self.S = []
        self.sum = 0
        rec = 4
        info = None
        total_length = 0
        if is_checked(start_east, start_north) and is_checked(end_east, end_north):
            rec = 0
            start_east, start_north, end_east, end_north = float(start_east), float(start_north), float(
                end_east), float(
                end_north)
            nearest_city_name = self.search_nearest_city(start_east, start_north)
            total_length = self.get_shortest_path(nearest_city_name, start_east, start_north, end_east, end_north)
        else:
            info = "error: 经纬度超出范围，请输入北纬4~53度，东经73~135度的参数。"
        dict_data = {
            "rec": rec,
            "total_length": round(total_length, 2),
            "info": info,
        }
        resp.data = json.dumps(dict_data)
        resp.status = falcon.HTTP_200

    def init_matrix(self):
        keys = self.conn.keys()
        self.n = len(keys)
        # count_o = 0
        self.matrix = [[0 for i in range(self.n)] for i in range(self.n)]
        for i, key in enumerate(keys):
            value = self.conn.hgetall(key)
            for j in range(self.n):
                old_i = int(value["id"])
                self.matrix[old_i][j] = float(value[str(j)])
        # print count_o
        self.matrix = np.array(self.matrix)

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

    def search_nearest_city(self, east_longitude, north_latitude):
        city_distance_list = []
        city_name_list = []
        nearby_city_list = self.search_geohash(east_longitude, north_latitude)
        # print nearby_city_list
        for city in nearby_city_list:
            city_distance = (city[1], geo_distance(city[2], city[3], east_longitude, north_latitude))
            city_distance_list.append(city_distance)
        # print city_distance_list
        # print sorted(city_distance_list, key=itemgetter(1))[:3]
        for city in sorted(city_distance_list, key=itemgetter(1))[:3]:
            city_name_list.append(city[0])
        return city_name_list[0]

    def get_shortest_path(self, city_name, start_east, start_north, end_east, end_north):
        value = self.conn.hgetall(city_name)
        self.sum += geo_distance(start_east, start_north, float(value["east"]), float(value["north"]))
        city_id = int(value["id"])
        # print "first city id:", city_id
        self.S.append(city_id)
        new_city_id = self.get_shortest_city(city_id)
        # new_city_id = 0
        while new_city_id is not None:
            # print len(self.S)
            self.S.append(new_city_id)
            city_id = new_city_id
            new_city_id = self.get_shortest_city(city_id)
            # print city_id, new_city_id
        for i in range(self.n - 1):
            self.sum += self.matrix[self.S[i]][self.S[i + 1]]
        last_city_name = self.get_city_name(city_id)
        value = self.conn.hgetall(last_city_name)
        self.sum += geo_distance(end_east, end_north, float(value["east"]), float(value["north"]))
        return self.sum

    def get_shortest_city(self, city_id):
        min_dist = 999999
        temp_min_dist = 999999
        next_city_id = None
        last_city_id = None
        for i in range(self.n):
            # print min_dist,i
            if self.matrix[i][city_id] < min_dist:
                if i not in self.S:
                    min_dist = self.matrix[i][city_id]
                    next_city_id = i
                elif i != city_id:
                    temp_min_dist = self.matrix[i][city_id]
                    last_city_id = i
        # print "next_city_id:{}, last_city_id:{}".format(next_city_id, last_city_id)
        if temp_min_dist < min_dist and last_city_id is not None:
            if 3 < len(self.S) - self.S.index(last_city_id) < 10:
                last_city_id = self.get_shortest_city_with_travel(last_city_id)
                if last_city_id is not None:
                    next_city_id = last_city_id
            else:
                pass
        return next_city_id

    def get_shortest_city_with_travel(self, city_id):
        self.temp_s = copy.deepcopy(self.S)
        pos = self.temp_s.index(city_id)
        new_city_list = copy.deepcopy(self.temp_s[pos:])
        n = len(new_city_list)
        dist = [[0 for i in range(n)] for i in range(n)]
        for i in range(n):
            for j in range(n):
                dist[i][j] = self.matrix[new_city_list[i]][new_city_list[j]]
        result = self.travel(dist)
        for i, id in enumerate(result[1]):
            self.temp_s[pos + i] = new_city_list[id]
        if self.temp_s != self.S:
            self.S = copy.deepcopy(self.temp_s)
            return self.S.pop()
        else:
            return None

    def travel(self, w):
        n = len(w)
        # valor inicial de 0 a todos los demas puntos
        A = {(frozenset([0, i + 1]), i + 1): (costo, [0, i + 1]) for i, costo in enumerate(w[0][1:])}
        for m in range(2, n):
            B = {}
            # en esta etapa se usa la recurisividad, ademas se utilizan el modulo 'combinations' que permite realizar
            # agrupaciones y comparaciones de datos.
            for S in [frozenset(C) | {0} for C in itertools.combinations(range(1, n), m)]:
                for j in S - {0}:
                    # se busca la ruta menos costosa para el viaje, es decir se buscan los valores minimos.
                    B[(S, j)] = min(
                        (A[(S - {j}, k)][0] + w[k][j], A[(S - {j}, k)][1] + [j]) for k in S if k != 0 and k != j)
            A = B
        # Ahora se agregan camino inicial y camino final
        res = min([(A[d][0] + w[0][d[1]], A[d][1]) for d in iter(A)])
        # Encontrado el valor minimo se tiene la solucion optima.

        # Resultado = res[0], [str(i) for i in res[1]]
        # con el ordenamiento de costos, se tiene solo que mostrar cual es la ruta a seguir en el viaje, es decir
        # se posicionan las ciudades en relacion con sus costos.
        return res

    def get_city_name(self, city_id):
        keys = self.conn.keys()
        for key in keys:
            value = self.conn.hgetall(key)
            if int(value['id']) == city_id:
                return key
