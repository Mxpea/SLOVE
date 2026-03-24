# S.L.O.V.E

Similarity Learning for Online Video Exploration（SLOVE）是一个基于内容相似度的视频推荐 Demo。

项目特点：

- 使用 TF-IDF 对视频标题与标签进行向量化。
- 使用余弦相似度进行推荐打分。
- 提供推荐结果与可视化数据接口。
- 前后端一体化，基于 Flask 启动即可体验。

说明：

- 本项目全程使用 AI 辅助开发。
- 首页效果部分复用了我的另一个项目 [WEB-MEController](https://github.com/Mxpea/WEB-MEController) 的代码。

## 技术栈

- Python 3.10+
- Flask
- pandas / numpy
- scikit-learn
- ECharts / ECharts-GL（前端可视化）

## 快速开始

1. 克隆项目并进入目录。
2. 创建虚拟环境并安装依赖。
3. 运行应用。

Windows（PowerShell）示例：

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

启动后访问：

- 首页：<http://127.0.0.1:5000/>
- Demo 页面：<http://127.0.0.1:5000/demo>
- 原理说明页：<http://127.0.0.1:5000/explain>

## 核心接口

- `GET /api/videos?limit=50&random=1`：获取视频列表。
- `GET /api/video/<video_id>`：获取单个视频详情。
- `POST /api/recommend`：根据历史行为返回推荐结果。
- `POST /api/visualize`：返回可视化所需节点与用户兴趣数据。
- `GET /api/docs/tree`：获取 docs 文档目录树。
- `GET /api/docs/content/<path>`：获取指定 markdown 文档内容。

推荐请求示例：

```json
{
  "history": [1, 5, 7],
  "top_n": 10
}
```

## 项目结构（简要）

```text
app.py                # Flask 服务入口
recommender.py        # 推荐算法与可视化数据生成
data/videos.csv       # 示例视频数据
templates/            # 页面模板
static/               # 前端脚本与样式
docs/                 # 项目文档
videodataset/         # 本地视频与数据处理脚本
```

## 数据集与引用

本项目使用了 [MicroLens 数据集](https://github.com/westlake-repl/MicroLens/)。

若你的研究或项目使用了相关数据，请引用原论文：

- 题目：A Content-Driven Micro-Video Recommendation Dataset at Scale
- 作者：Yongxin Ni, Yu Cheng, Xiangyan Liu, Junchen Fu, Youhua Li, Xiangnan He, et al.
- 发表：arXiv preprint arXiv:2309.15379 (2023)
- 链接：<https://arxiv.org/abs/2309.15379>

BibTeX：

```bibtex
@article{ni2023content,
  title={A Content-Driven Micro-Video Recommendation Dataset at Scale},
  author={Ni, Yongxin and Cheng, Yu and Liu, Xiangyan and Fu, Junchen and Li, Youhua and He, Xiangnan and others},
  journal={arXiv preprint arXiv:2309.15379},
  year={2023}
}
```
