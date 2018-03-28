# -*- coding: utf-8 -*-
import json

__author__ = "zyqzyq"
if __name__ == '__main__':
    data_json = {"city": []}
    with open('citylist.txt') as f:
        for line in f:
            # print line
            city_list = line.split(";")
            for city in city_list:
                info_list = city.split(" ")
                if len(info_list) == 3 and info_list[1] != '':
                    data = []
                    # print info_list
                    for i in range(3):
                        if len(info_list[i].split(":"))>1:
                            data.append(info_list[i].split(":")[1])
                    # dict = {data[0][6:]: [float(data[1]), float(data[2])]}
                    # print dict
                    data_json["city"].append({"name": (data[0][4:]).decode('gbk'), "value": [float(data[1]), float(data[2])]})
                    #print data_json
    with open("citydata.txt", "wb") as wf:
        print data_json
        wf.write(json.dumps(data_json))
