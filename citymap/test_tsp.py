# -*- coding: utf-8 -*-
import time

import datetime

__author__ = "zyqzyq"
__time__ = '2018/4/2 11:00'

import numpy as np
import redis
import copy
from functools import wraps
import itertools


class TSP:
    def __init__(self):
        self.pool = redis.ConnectionPool(host='127.0.0.1', port=6379)
        self.conn = redis.Redis(connection_pool=self.pool)
        self.n = 625
        self.init_matrix()
        self.temp_s = []

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

    # def get_shortest_city(self, city_id):
    #     min_dist = 999999
    #     next_city_id = None
    #     for i in range(self.n):
    #         if self.matrix[i][city_id] < min_dist and (i not in self.S):
    #             min_dist = self.matrix[i][city_id]
    #             next_city_id = i
    #     return next_city_id
    def get_nearest_way(self, city_num):
        city_list = [i for i in range(city_num)]

    def get_shortest_path(self, city_id):
        self.S= [0]
        # print "first city id:", city_id
        new_city_id = self.get_shortest_city(city_id)
        # new_city_id = 0
        while new_city_id is not None:
            # print len(self.S)
            self.S.append(new_city_id)
            city_id = new_city_id
            new_city_id = self.get_shortest_city(city_id)
            # print city_id, new_city_id



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
            self.temp_s[pos+i] = new_city_list[id]
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


if __name__ == '__main__':
    tsp = TSP()
    starttime = datetime.datetime.now()
    tsp.get_shortest_path(0)
    endtime = datetime.datetime.now()
    print "runtime:", (endtime - starttime).seconds
