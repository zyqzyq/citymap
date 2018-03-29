# -*- coding: utf-8 -*-

__author__ = "zyqzyq"
__time__ = '2018/3/29 13:18'
import requests
import json
if __name__ == '__main__':
    url = "http://127.0.0.1:8000/city/31/117"
    # data = {"hello": "world","content":"wwww"}
    d = requests.post(url)
    print d
    print d.text
    data = json.loads(d.text)
    for city in data["city_list"]:
        print city