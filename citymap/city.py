# -*- coding: utf-8 -*-


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
        self.data = {"city": []}

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
        self.get_data()
        # print self.data
        resp.data = json.dumps(self.data)
        resp.status = falcon.HTTP_200

    def get_data(self):
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
                data = {"name": result[1], "value": [result[2], result[3]]}
                self.data["city"].append(data)
            # print self.data
        except:
            # 发生错误时回滚
            print  "Error: unable to fecth data"

        # 关闭数据库连接
        db.close()
