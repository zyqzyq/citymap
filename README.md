# 计划
使用Python、Falcon、Nginx、MySQL、Redis、eCharts等或其他框架构建一个简单的Web应用

# 目标功能：
- 构造一份中国各个城市对应的所有的经纬度点形成一个地图展现在Web应用上
- 给予一个具体的经纬度点，在地图上构建该点到离该点最近的3个城市的最短路径
- 给予两个经纬度的点（起点和终点），在地图上构建起点到终点的最短路径（即起点通向终点依次穿过地图上的城市，最终连接所有点形成一条路径，要求路径最短，且给出最短路径距离多少Km）

[思路及代码片段](https://github.com/zyqzyq/citymap/blob/master/README.md)

# 进度
    实现falcon mysql redis存储数据
    实现html显示地图与所有二级城市
    实现找寻确定点的最近的3个城市
    
![](https://raw.githubusercontent.com/zyqzyq/citymap/master/screenshots/1.png)

    实现根据经纬度查询最近的3座城市
![](https://raw.githubusercontent.com/zyqzyq/citymap/master/screenshots/2.png)

    根据2个点的经纬度球最短路径
![](https://raw.githubusercontent.com/zyqzyq/citymap/master/screenshots/3.png)


# 计划：
- [x] -  使用eCharts显示地图
- [x] -  计算点与点之间最短路径
- [x] -  邮差问题问题

# TODO
增加测试模块



