# -*- coding: UTF-8 -*-
import falcon
from falcon import testing
import pytest
from app import api
import json


@pytest.fixture
def client():
    return testing.TestClient(api)


def test_city_list(client):
    response = client.simulate_get('/city')
    doc = '{"count": 20, "city": [{"name": "\u6c55\u5934", "value": [116.41, 23.22]}, {"name": "\u4e73\u5c71", "value": [121.31, 36.54]}, {"name": "\u7f57\u5b9a", "value": [111.33, 22.46]}, {"name": "\u5f00\u539f", "value": [124.02, 42.32]}, {"name": "\u9879\u57ce", "value": [114.54, 33.26]}, {"name": "\u53f0\u5317\u5e02", "value": [121.3, 25.03]}, {"name": "\u65e5\u7167", "value": [119.32, 35.23]}, {"name": "\u592a\u539f", "value": [112.33, 37.54]}, {"name": "\u6e5b\u6c5f", "value": [110.24, 21.11]}, {"name": "\u4e34\u6d77", "value": [121.08, 28.51]}, {"name": "\u897f\u5b89", "value": [108.57, 34.17]}, {"name": "\u5b89\u4e18", "value": [119.12, 36.25]}, {"name": "\u5b9c\u5174", "value": [119.49, 31.21]}, {"name": "\u4e03\u53f0\u6cb3", "value": [130.49, 45.48]}, {"name": "\u6fb3\u95e8\u5e02", "value": [115.07, 21.33]}, {"name": "\u5927\u8fde", "value": [121.36, 38.55]}, {"name": "\u56fe\u4eec", "value": [129.51, 42.57]}, {"name": "\u5982\u768b", "value": [120.33, 32.23]}, {"name": "\u798f\u6e05", "value": [119.23, 25.42]}, {"name": "\u90b5\u6b66", "value": [117.29, 27.2]}], "next_page_url": "http://localhost:8000/city?page=2&num=20"}'
    assert response.status == falcon.HTTP_OK
    assert response.content == doc


def test_city_list_wrong_type(client):
    response = client.simulate_get('/city', query_string="page=ppp")
    doc = '{"title": "Invalid parameter", "description": "The \\"page\\" parameter is invalid. The value must be an integer."}'
    assert response.content == doc
    assert response.status == falcon.HTTP_400


def test_city_list_with_negative_num(client):
    response = client.simulate_get('/city', query_string="page=-1")
    doc = '{"count": null, "city": [], "next_page_url": null}'
    assert response.content == doc
    assert response.status == falcon.HTTP_200


def test_city_list_with_out_of_range(client):
    response = client.simulate_get('/city', query_string="page=9999")
    doc = '{"count": null, "city": [], "next_page_url": null}'
    assert response.content == doc
    assert response.status == falcon.HTTP_200


def test_search_nearby_city(client):
    response = client.simulate_get('/search/77/33')
    doc = {"info": None, "rec": 0, "city_list": ["和田","喀什","日喀则"]}
    assert response.content == json.dumps(doc)
    assert response.status == falcon.HTTP_200

def test_search_nearby_with_point(client):
    response = client.simulate_get('/search/77.66/33.99')
    doc = {"info": None, "rec": 0, "city_list": ["和田","喀什","日喀则"]}
    assert response.content == json.dumps(doc)
    assert response.status == falcon.HTTP_200

def test_search_nearby_city_out_of_range(client):
    response = client.simulate_get('/search/90/56')
    doc = {"info": "error: 经纬度超出范围，请输入北纬4~53度，东经73~135度的参数。", "rec": 4, "city_list": []}
    assert response.content == json.dumps(doc)
    assert response.status == falcon.HTTP_200


def test_search_nearby_city_with_wrong_type(client):
    response = client.simulate_get('/search/aa/bb')
    doc = {"info": "error: 经纬度超出范围，请输入北纬4~53度，东经73~135度的参数。", "rec": 4, "city_list": []}
    assert response.content == json.dumps(doc)
    assert response.status == falcon.HTTP_200


def test_search_nearby_city_with_negative_num(client):
    response = client.simulate_get('/search/-77/-33')
    doc = {"info": "error: 经纬度超出范围，请输入北纬4~53度，东经73~135度的参数。", "rec": 4, "city_list": []}
    assert response.content == json.dumps(doc)
    assert response.status == falcon.HTTP_200


def test_tsp_city(client):
    response = client.simulate_get('/tsp/77/33/99/44')
    doc = {"info": None, "rec": 0, "total_length": 60643.14}
    assert response.content == json.dumps(doc)
    assert response.status == falcon.HTTP_200


def test_tsp_city_with_wrong_type(client):
    response = client.simulate_get('/tsp/aa/bb/cc/dd')
    doc = {"info": "error: 经纬度超出范围，请输入北纬4~53度，东经73~135度的参数。", "rec": 4, "total_length": 0.0}
    assert response.content == json.dumps(doc)
    assert response.status == falcon.HTTP_200


def test_tsp_city_out_of_range(client):
    response = client.simulate_get('/tsp/99/99/99/99')
    doc = {"info": "error: 经纬度超出范围，请输入北纬4~53度，东经73~135度的参数。", "rec": 4, "total_length": 0.0}
    assert response.content == json.dumps(doc)
    assert response.status == falcon.HTTP_200

def test_tsp_city_with_nagetive_num(client):
    response = client.simulate_get('/tsp/-77/33/99/44')
    doc = {"info": "error: 经纬度超出范围，请输入北纬4~53度，东经73~135度的参数。", "rec": 4, "total_length": 0.0}
    assert response.content == json.dumps(doc)
    assert response.status == falcon.HTTP_200