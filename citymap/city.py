# -*- coding: utf-8 -*-


__author__ = "zyqzyq"
__time__ = '2018/3/27 11:26'

import msgpack
import falcon
import json


class CityResource(object):

    def on_get(self, req, resp):
        myData = {"city": [

            {"name": '海门', "value": [121.15, 31.89, 90]},
            {"name": '鄂尔多斯', "value": [109.781327, 39.608266, 120]},
            {"name": '招远', "value": [120.38, 37.35, 142]},
            {"name": '舟山', "value": [122.207216, 29.985295, 123]},
        ]
        }
        resp.data = (json.dumps(myData))
        # resp.content_type = 'application/msgpack'
        resp.status = falcon.HTTP_200
