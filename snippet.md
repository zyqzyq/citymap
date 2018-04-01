# 思路
- falcon 实现restful
- mysql redis 实现数据存储
- echarts 显示地图
- JavaScript 获取后端数据并进行显示

### 显示map
- echarts 显示地图
- JavaScript 获取后端数据用echarts散点图显示

### 计算最近城市
- 调用geohash 匹配从mysql中匹配搜索
- 从搜索结果中筛选最近的3个城市

### 计算最短路径
- 先计算起点最近的城市
- 使用贪心算法计算离当前城市最近的城市，直到所有城市都被加入已选城市
- 计算最后城市到终点的距离

# sinppet

   根据page和每页数量num从redis 获取数据
```
    def get_data(self, page, num):
        city_list = []
        keys = self.conn.keys()
        if page * num < len(keys):
            count = num
            next_page_url = "http://localhost:8000/city?page={}&num={}".format(page + 1, num)
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
```

   根据给定的经纬度通过geohash从mysql搜索附近城市的列表，再计算出最佳的3个城市
```
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
```

    初始化各城市距离二维数组
```
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
```
   
       获取最短路径
       - 找出离起点最近的城市
       - 循环从未选城市中计算离当前城市最近城市
       - 计算最后一个城市到终点位置
```
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
            self.sum += self.matrix[city_id][new_city_id]
            self.S.append(new_city_id)
            city_id = new_city_id
            new_city_id = self.get_shortest_city(city_id)
            # print city_id, new_city_id
        last_city_name = self.get_city_name(city_id)
        value = self.conn.hgetall(last_city_name)
        self.sum += geo_distance(end_east, end_north, float(value["east"]), float(value["north"]))
        return self.sum

    def get_shortest_city(self, city_id):
        min_dist = 999999
        next_city_id = None
        for i in range(self.n):
            # print min_dist,i
            if self.matrix[i][city_id] < min_dist and (i not in self.S):
                min_dist = self.matrix[i][city_id]
                next_city_id = i
        return next_city_id
```

