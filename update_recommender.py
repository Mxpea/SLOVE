with open('recommender.py', 'r', encoding='utf-8') as f:
    code = f.read()

import re
code = code.replace('from sklearn.metrics.pairwise import cosine_similarity', 'from sklearn.metrics.pairwise import cosine_similarity\nfrom sklearn.decomposition import PCA')
code = code.replace(
    "self.idx_to_video_id = {idx: vid for idx, vid in enumerate(self.df['video_id'])}",
    """self.idx_to_video_id = {idx: vid for idx, vid in enumerate(self.df['video_id'])}

        # 使用 PCA 将高维向量降维至 2D，用于前端可视化
        self.pca = PCA(n_components=2)
        if len(self.video_vectors) > 2:
            self.video_coords_2d = self.pca.fit_transform(self.video_vectors)
        else:
            self.video_coords_2d = np.zeros((len(self.video_vectors), 2))
        
        # 获取特征词汇表映射 (索引 -> 词语)
        self.feature_names = self.vectorizer.get_feature_names_out()"""
)

# Also add methods to get the visualization data
methods = """
    def get_visualization_data(self, history_ids):
        # 返回所有视频的 2D 坐标
        nodes = []
        for i in range(len(self.video_vectors)):
            nodes.append({
                'video_id': int(self.df.iloc[i]['video_id']),
                'title': str(self.df.iloc[i]['title']),
                'tags': str(self.df.iloc[i]['tags']),
                'x': float(self.video_coords_2d[i, 0]),
                'y': float(self.video_coords_2d[i, 1])
            })
        
        user_node = None
        if history_ids:
            indices = [self.video_id_to_idx[vid] for vid in history_ids if vid in self.video_id_to_idx]
            if indices:
                history_vectors = self.video_vectors[indices]
                user_vector = np.mean(history_vectors, axis=0).reshape(1, -1)
                user_coord = self.pca.transform(user_vector)[0]
                
                # 获取用户的 Top Keyword
                top_k = 10
                top_keyword_indices = user_vector[0].argsort()[::-1][:top_k]
                user_keywords = [{'word': str(self.feature_names[idx]), 'weight': float(user_vector[0, idx])} 
                                 for idx in top_keyword_indices if user_vector[0, idx] > 0]
                
                user_node = {
                    'x': float(user_coord[0]),
                    'y': float(user_coord[1]),
                    'keywords': user_keywords
                }
                
                # 计算每个节点与用户的距离（用于辅助可视化）
                for node in nodes:
                    idx = self.video_id_to_idx[node['video_id']]
                    node['similarity'] = float(cosine_similarity(user_vector, self.video_vectors[idx].reshape(1, -1))[0][0])
                
        return {'videos': nodes, 'user': user_node}
"""

if "def get_visualization_data" not in code:
    code += methods

with open('recommender.py', 'w', encoding='utf-8') as f:
    f.write(code)
