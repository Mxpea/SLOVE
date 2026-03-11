import os
from flask import Flask, jsonify, request, render_template
from recommender import VideoRecommender

app = Flask(__name__)

# 获取当前文件所在真实目录，确保系统在任何路径下启动都能正确加载相对路径下的CSV
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, 'data', 'videos.csv')

# 系统启动时加载数据和生成TF-IDF矩阵
recommender = VideoRecommender(CSV_PATH)

# --- 页面路由 (Frontend) ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video/<int:video_id>')
def video(video_id):
    return render_template('video.html', video_id=video_id)

@app.route('/explain')
def explain():
    return render_template('explain.html')

# --- API 路由 (Backend) ---

@app.route('/api/videos', methods=['GET'])
def api_videos():
    """获取视频列表"""
    return jsonify(recommender.get_all_videos())

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
    recommendations = recommender.recommend(history)
    
    return jsonify({
        "recommendations": recommendations
    })

if __name__ == '__main__':
    print("启动人工智能推荐系统 Demo...")
    app.run(host='0.0.0.0', port=5000, debug=True)