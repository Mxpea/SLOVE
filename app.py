import os
from flask import Flask, jsonify, request, render_template, send_from_directory
from recommender import VideoRecommender

app = Flask(__name__)

# 获取当前文件所在真实目录，确保系统在任何路径下启动都能正确加载相对路径下的CSV
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, 'data', 'videos.csv')
VIDEO_DIR = os.path.join(BASE_DIR, 'videodataset')

# 系统启动时加载数据和生成TF-IDF矩阵
recommender = VideoRecommender(CSV_PATH)

# --- 页面路由 (Frontend) ---

@app.route('/icon.png')
def serve_icon():
    return send_from_directory(BASE_DIR, 'icon.png')

@app.route('/')
def home():
    # 强制将根目录那个带 3D 特效的 index.html 设为首页
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/<filename>')
def serve_root_files(filename):
    # 使加载 3D 模型文件 (inner.glb, outer.glb) 不会报 404
    if filename.endswith('.glb'):
        return send_from_directory(BASE_DIR, filename)
    return "Not Found", 404

@app.route('/demo')
def demo():
    # 点进系统后展示的是推荐列表页
    return render_template('demo.html')

@app.route('/video/<int:video_id>')
def video(video_id):
    return render_template('video.html', video_id=video_id)

@app.route('/explain')
def explain():
    return render_template('explain.html')

# --- 文档站 API ---
def get_docs_tree(dir_path, base_path=""):
    tree = []
    if not os.path.exists(dir_path):
        return tree
    
    entries = sorted(os.listdir(dir_path))
    for entry in entries:
        full_path = os.path.join(dir_path, entry)
        rel_path = os.path.join(base_path, entry).replace('\\', '/')
        
        if os.path.isdir(full_path):
            children = get_docs_tree(full_path, rel_path)
            if children:  # 只有该目录下有md文件才加入
                tree.append({
                    "name": entry,
                    "type": "dir",
                    "path": rel_path,
                    "children": children
                })
        elif os.path.isfile(full_path) and entry.endswith('.md'):
            tree.append({
                "name": entry.replace('.md', ''),
                "type": "file",
                "path": rel_path
            })
    return tree

@app.route('/api/docs/tree', methods=['GET'])
def api_docs_tree():
    """获取文档结构树"""
    docs_dir = os.path.join(BASE_DIR, 'docs')
    tree = get_docs_tree(docs_dir)
    return jsonify(tree)

@app.route('/api/docs/content/<path:filepath>', methods=['GET'])
def api_docs_content(filepath):
    """获取具体文档的内容"""
    docs_dir = os.path.join(BASE_DIR, 'docs')
    # 安全处理，防止目录穿越
    safe_path = os.path.abspath(os.path.join(docs_dir, filepath))
    if not safe_path.startswith(os.path.abspath(docs_dir)):
        return jsonify({"error": "Unauthorized"}), 403
    
    if not os.path.exists(safe_path) or not safe_path.endswith('.md'):
        return jsonify({"error": "Not Found"}), 404
        
    with open(safe_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return jsonify({"content": content})

# 提供本地视频文件的访问路由
@app.route('/videodataset/<filename>')
def serve_video(filename):
    return send_from_directory(VIDEO_DIR, filename)

# --- API 路由 (Backend) ---

@app.route('/api/videos', methods=['GET'])
def api_videos():
    """获取视频列表"""
    limit = int(request.args.get('limit', 50))
    randomize = request.args.get('random', '0') == '1'
    return jsonify(recommender.get_all_videos(limit=limit, randomize=randomize))

@app.route('/api/video/<int:video_id>', methods=['GET'])
def api_video(video_id):
    """获取单个视频详情"""
    video = recommender.get_video(video_id)
    if video:
        return jsonify(video)
    return jsonify({"error": "Video not found"}), 404

@app.route('/api/recommend', methods=['POST'])
def api_recommend():
    """
    推荐接口
    输入: {"history": [1, 5, 7]}
    输出: {"recommendations": [{"video_id": 12, "score": 0.87}, ...]}
    服务器不持久化存储用户信息，只基于此请求中的历史记录计算。
    """
    data = request.json
    if not data or 'history' not in data:
        return jsonify({"error": "Missing history"}), 400
        
    history = data['history']
    top_n = data.get('top_n', 10)  # 默认多给一些方便前台自适应
    recommendations = recommender.recommend(history, top_n=top_n)

    return jsonify({
        "recommendations": recommendations
    })

@app.route('/api/visualize', methods=['POST'])
def api_visualize():
    data = request.json or {}
    history = data.get('history', [])
    vis_data = recommender.get_visualization_data(history)
    return jsonify(vis_data)

if __name__ == '__main__':
    print("正在启动...")
    # 关闭 debug 模式以提升生产环境的执行效率和安全性
    app.run(host='0.0.0.0', port=5000, debug=False)
