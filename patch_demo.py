with open('templates/demo.html', 'r', encoding='utf-8') as f:
    html = f.read()

viz_container = """
    <div class="container">
        <h2 class="section-title">> 向量空间分布模型 <span style="font-size: 0.5em; color: rgba(255,255,255,0.5);">[2D PCA Projection]</span></h2>
        <div id="vector-viz" style="width: 100%; height: 450px; background: rgba(5,3,10,0.6); border: 1px solid rgba(0,246,255,0.2); border-radius: 4px; box-shadow: 0 0 15px rgba(0,246,255,0.1); margin-bottom: 40px; position: relative;">
            <div id="viz-loading" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: #00f6ff; font-family: monospace; animation: pulse 1.5s infinite;">
                模型数据降维中 (LOADING PCA)...
            </div>
        </div>
"""

html = html.replace('<div class="container">', viz_container)

html = html.replace('</head>', '    <script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>\n</head>')

js_code = """
            // 3. 渲染数据可视化
            fetch('/api/visualize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ history: history })
            })
            .then(res => res.json())
            .then(data => {
                document.getElementById('viz-loading').style.display = 'none';
                const chart = echarts.init(document.getElementById('vector-viz'));
                
                const seriesData = [{
                    name: '全部视频',
                    type: 'scatter',
                    symbolSize: function(val) {
                        return val[4] > 0.1 ? 16 : 8; // If similar, larger symbol
                    },
                    itemStyle: {
                        color: 'rgba(0, 246, 255, 0.6)',
                        shadowBlur: 10,
                        shadowColor: '#00f6ff'
                    },
                    data: data.videos.map(v => ({
                        value: [v.x, v.y, v.title, v.tags, v.similarity || 0, v.video_id],
                        itemStyle: {
                            color: v.similarity && v.similarity > 0.1 ? 'rgba(255, 43, 214, 0.8)' : 'rgba(0, 246, 255, 0.6)',
                            shadowColor: v.similarity && v.similarity > 0.1 ? '#ff2bd6' : '#00f6ff'
                        }
                    }))
                }];

                if (data.user) {
                    seriesData.push({
                        name: '用户特征坐标',
                        type: 'effectScatter',
                        symbolSize: 22,
                        itemStyle: {
                            color: '#ff2bd6',
                            shadowBlur: 20,
                            shadowColor: '#ff2bd6'
                        },
                        data: [{
                            value: [data.user.x, data.user.y, 'User Vector']
                        }]
                    });
                }

                const option = {
                    backgroundColor: 'transparent',
                    tooltip: {
                        backgroundColor: 'rgba(5, 3, 10, 0.9)',
                        borderColor: '#00f6ff',
                        textStyle: { color: '#fff' },
                        formatter: function (param) {
                            if (param.seriesName === '用户特征坐标') {
                                let tip = '<strong style="color:#ff2bd6;">[ 用户特征雷达 (User Vector) ]</strong><br/>';
                                data.user.keywords.forEach(kw => {
                                    tip += `${kw.word}: ${(kw.weight).toFixed(4)}<br/>`;
                                });
                                return tip;
                            }
                            const val = param.data.value;
                            return `
                                <strong style="color:#00f6ff">${val[2]}</strong><br/>
                                <span style="color:rgba(255,255,255,0.6)">标签: ${val[3]}</span><br/>
                                ${val[4] > 0 ? `<span style="color:#ff2bd6">匹配度: ${(val[4]*100).toFixed(1)}%</span>` : ''}
                            `;
                        }
                    },
                    grid: {
                        left: '2%', right: '2%', top: '5%', bottom: '5%'
                    },
                    xAxis: {
                        type: 'value',
                        splitLine: { lineStyle: { color: 'rgba(0, 246, 255, 0.1)', type: 'dashed' } },
                        axisLabel: { show: false }
                    },
                    yAxis: {
                        type: 'value',
                        splitLine: { lineStyle: { color: 'rgba(0, 246, 255, 0.1)', type: 'dashed' } },
                        axisLabel: { show: false }
                    },
                    series: seriesData
                };

                chart.setOption(option);
                
                chart.on('click', function(params) {
                    if (params.seriesName === '全部视频') {
                        window.location.href = `/video/${params.data.value[5]}`;
                    }
                });

                window.addEventListener('resize', () => {
                    chart.resize();
                });
            })
            .catch(err => {
                document.getElementById('viz-loading').innerText = '模型降维失败或数据不存在';
            });
"""

html = html.replace('// 1. 获取所有视频', js_code + '\n            // 1. 获取所有视频')

with open('templates/demo.html', 'w', encoding='utf-8') as f:
    f.write(html)
