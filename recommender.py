import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA

class VideoRecommender:
    def __init__(self, data_path):
        # 1. 加载数据
        self.df = pd.read_csv(data_path)
        
        # 统一处理列名差异：如果 CSV 含有 'id' 或 'tag'，将其重命名为我们需要使用的标准名
        if 'id' in self.df.columns:
            self.df.rename(columns={'id': 'video_id'}, inplace=True)
        if 'tag' in self.df.columns:
            self.df.rename(columns={'tag': 'tags'}, inplace=True)
        
        # 填充缺失值为字符串空，防止字符串拼接报错
        self.df['title'] = self.df['title'].fillna('')
        self.df['tags'] = self.df['tags'].fillna('')

        # 2. 数据预处理：文本合并 (Title + Tags)
        self.df['text'] = self.df['title'] + " " + self.df['tags']
        
        # 3. 视频向量化：使用 TF-IDF
        self.vectorizer = TfidfVectorizer()
        self.tfidf_matrix = self.vectorizer.fit_transform(self.df['text'])
        self.video_vectors = self.tfidf_matrix.toarray()
        
        # 建立 video_id 到 索引 的映射，方便查找
        self.video_id_to_idx = {vid: idx for idx, vid in enumerate(self.df['video_id'])}
        self.idx_to_video_id = {idx: vid for idx, vid in enumerate(self.df['video_id'])}

        # 使用 PCA 将高维向量降维至 3D，用于前端可视化(同时兼容 2D/3D)
        n_comp = min(3, len(self.video_vectors)) if len(self.video_vectors) > 0 else 1
        self.pca = PCA(n_components=n_comp)
        
        self.video_coords_3d = np.zeros((len(self.video_vectors), 3))
        if len(self.video_vectors) > 0:
            coords = self.pca.fit_transform(self.video_vectors)
            self.video_coords_3d[:, :n_comp] = coords
        
        # 获取特征词汇表映射 (索引 -> 词语)
        self.feature_names = self.vectorizer.get_feature_names_out()

    def get_all_videos(self, limit=50):
        """返回所有视频信息"""
        # 防止你的 videos.csv 数据量太大(上万条)时瞬间传给前端导致浏览器直接卡死崩溃
        # 我们在这里做了一个截断，列表页随机(或按顺序)展示 50 条用于演示即可
        return self.df[['video_id', 'title', 'tags']].head(limit).to_dict(orient='records')

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
    def get_visualization_data(self, history_ids):
        # 返回所有视频的 3D 坐标
        nodes = []
        for i in range(len(self.video_vectors)):
            nodes.append({
                'video_id': int(self.df.iloc[i]['video_id']),
                'title': str(self.df.iloc[i]['title']),
                'tags': str(self.df.iloc[i]['tags']),
                'x': float(self.video_coords_3d[i, 0]),
                'y': float(self.video_coords_3d[i, 1]),
                'z': float(self.video_coords_3d[i, 2])
            })
        
        user_node = None
        if history_ids:
            indices = [self.video_id_to_idx[vid] for vid in history_ids if vid in self.video_id_to_idx]
            if indices:
                history_vectors = self.video_vectors[indices]
                user_vector = np.mean(history_vectors, axis=0).reshape(1, -1)
                user_coord_raw = self.pca.transform(user_vector)[0]
                user_coord = np.zeros(3)
                user_coord[:len(user_coord_raw)] = user_coord_raw

                # 获取用户的 Top Keyword
                top_k = 10
                top_keyword_indices = user_vector[0].argsort()[::-1][:top_k]
                user_keywords = [{'word': str(self.feature_names[idx]), 'weight': float(user_vector[0, idx])}
                                 for idx in top_keyword_indices if user_vector[0, idx] > 0]

                user_node = {
                    'x': float(user_coord[0]),
                    'y': float(user_coord[1]),
                    'z': float(user_coord[2]),
                    'keywords': user_keywords
                }
                
                # 计算每个节点与用户的距离（用于辅助可视化）
                sims = cosine_similarity(user_vector, self.video_vectors)[0]
                for i, node in enumerate(nodes):
                    node['similarity'] = float(sims[i])
        return {'videos': nodes, 'user': user_node}
