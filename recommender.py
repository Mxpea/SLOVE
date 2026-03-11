import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class VideoRecommender:
    def __init__(self, data_path):
        # 1. 加载数据
        self.df = pd.read_csv(data_path)
        
        # 2. 数据预处理：文本合并 (Title + Tags)
        self.df['text'] = self.df['title'] + " " + self.df['tags']
        
        # 3. 视频向量化：使用 TF-IDF
        self.vectorizer = TfidfVectorizer()
        self.tfidf_matrix = self.vectorizer.fit_transform(self.df['text'])
        self.video_vectors = self.tfidf_matrix.toarray()
        
        # 建立 video_id 到 索引 的映射，方便查找
        self.video_id_to_idx = {vid: idx for idx, vid in enumerate(self.df['video_id'])}
        self.idx_to_video_id = {idx: vid for idx, vid in enumerate(self.df['video_id'])}

    def get_all_videos(self):
        """返回所有视频信息"""
        return self.df[['video_id', 'title', 'tags']].to_dict(orient='records')

    def get_video(self, video_id):
        """获取单个视频信息"""
        row = self.df[self.df['video_id'] == video_id]
        if not row.empty:
            return row.iloc[0].to_dict()
        return None

    def recommend(self, history_ids, top_n=5):
        """根据播放历史推荐视频，数学原理体现：TF-IDF、向量平均、余弦相似度"""
        if not history_ids:
            return []
        
        # 提取历史视频的索引
        indices = [self.video_id_to_idx[vid] for vid in history_ids if vid in self.video_id_to_idx]
        if not indices:
            return []
            
        # 获得用户观看过的所有视频的向量
        history_vectors = self.video_vectors[indices]
        
        # 4. 用户兴趣向量生成：向量平均
        # 数学表达: U = (V1 + V2 + ... + Vn) / n
        user_vector = np.mean(history_vectors, axis=0).reshape(1, -1)
        
        # 5. 相似度计算：余弦相似度
        similarities = cosine_similarity(user_vector, self.video_vectors)[0]
        
        # 将已经看过的视频相似度设为一个极小值（防止推荐已看过的视频）
        for idx in indices:
            similarities[idx] = -1
            
        # 获取 Top-N 相似度的索引
        top_indices = np.argsort(similarities)[::-1][:top_n]
        
        # 6. 生成推荐结果
        recommendations = []
        for idx in top_indices:
            score = float(similarities[idx])
            if score > 0:
                recommendations.append({
                    "video_id": int(self.df.iloc[idx]['video_id']),
                    "title": str(self.df.iloc[idx]['title']),
                    "tags": str(self.df.iloc[idx]['tags']),
                    "score": round(score, 4)
                })
                
        return recommendations