# -*- coding: utf-8 -*-
import redis

__author__ = "zyqzyq"
__time__ = '2018/3/27 11:26'

import falcon
import MySQLdb
import json


class CORSComponent(object):
    def process_response(self, req, resp, resource, req_succeeded):
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


class CityResource(object):

    def __init__(self):
        self.pool = redis.ConnectionPool(host='127.0.0.1', port=6379)
        self.conn = redis.Redis(connection_pool=self.pool)
        self.init_redis()
        self.city_list = []
        self.count = 0
        self.next_page_url = None

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
        self.get_data(page, num)
        # print len(self.data["city"])
        dict_data = {
            "city": self.city_list,
            "count": self.count,
            "next_page_url": self.next_page_url,
        }

        resp.data = json.dumps(dict_data)
        resp.status = falcon.HTTP_200

    def get_data(self, page, num):
        self.city_list = []
        keys = self.conn.keys()
        if page*num < len(keys):
            self.count = num
            self.next_page_url = "http://127.0.0.1:8000/city?page={}&num={}".format(page+1, num)
            for key in keys[(page-1)*num:page*num]:
                value = self.conn.hgetall(key)
                self.city_list.append({"name": key, "value": [float(value["1"]), float(value["2"])]})
        elif (page-1)*num < len(keys) < page*num:
            self.count = page*num - len(keys)
            self.next_page_url = None
            for key in keys[(page - 1) * num:]:
                value = self.conn.hgetall(key)
                self.city_list.append({"name": key, "value": [float(value["1"]), float(value["2"])]})
        else:
            self.count = None
            self.next_page_url = None


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
