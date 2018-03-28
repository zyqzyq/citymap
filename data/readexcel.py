# -*- coding: utf-8 -*-
import json

__author__ = "zyqzyq"

import xlrd

if __name__ == '__main__':
    data_json = {"city": []}
    ExcelFile = xlrd.open_workbook("citylist.xls")
    print ExcelFile.sheet_names()
    sheet = ExcelFile.sheet_by_index(0)
    print sheet.name, sheet.nrows, sheet.ncols
    for i in range(1, sheet.nrows):
        data = {"name": sheet.cell(i, 1).value, "value": [sheet.cell(i, 3).value, sheet.cell(i, 2).value]}
        data_json["city"].append(data)
    print data_json
    with open("citydata.txt", "wb") as wf:
        wf.write(json.dumps(data_json))
