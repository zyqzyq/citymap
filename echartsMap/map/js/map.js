// 初始化echarts示例mapChart
var mapChart = echarts.init(document.getElementById('map-wrap'));

// mapChart的配置
var option = {
    geo: {
        map: 'china'
    }
};
mapChart.setOption(option);