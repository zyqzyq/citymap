# -*- coding: UTF-8 -*-
import falcon
from falcon import testing
import pytest
import msgpack
from app import api


@pytest.fixture
def client():
    return testing.TestClient(api)


def test_city_list(client):
    response = client.simulate_get('/city')
    doc = '{"count": 20, "city": [{"name": "\u6c55\u5934", "value": [116.41, 23.22]}, {"name": "\u4e73\u5c71", "value": [121.31, 36.54]}, {"name": "\u7f57\u5b9a", "value": [111.33, 22.46]}, {"name": "\u5f00\u539f", "value": [124.02, 42.32]}, {"name": "\u9879\u57ce", "value": [114.54, 33.26]}, {"name": "\u53f0\u5317\u5e02", "value": [121.3, 25.03]}, {"name": "\u65e5\u7167", "value": [119.32, 35.23]}, {"name": "\u592a\u539f", "value": [112.33, 37.54]}, {"name": "\u6e5b\u6c5f", "value": [110.24, 21.11]}, {"name": "\u4e34\u6d77", "value": [121.08, 28.51]}, {"name": "\u897f\u5b89", "value": [108.57, 34.17]}, {"name": "\u5b89\u4e18", "value": [119.12, 36.25]}, {"name": "\u5b9c\u5174", "value": [119.49, 31.21]}, {"name": "\u4e03\u53f0\u6cb3", "value": [130.49, 45.48]}, {"name": "\u6fb3\u95e8\u5e02", "value": [115.07, 21.33]}, {"name": "\u5927\u8fde", "value": [121.36, 38.55]}, {"name": "\u56fe\u4eec", "value": [129.51, 42.57]}, {"name": "\u5982\u768b", "value": [120.33, 32.23]}, {"name": "\u798f\u6e05", "value": [119.23, 25.42]}, {"name": "\u90b5\u6b66", "value": [117.29, 27.2]}], "next_page_url": "http://localhost:8000/city?page=2&num=20"}'
    assert response.status == falcon.HTTP_OK
    assert response.content == doc
