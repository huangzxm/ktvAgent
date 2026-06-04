
"""
FAISS 向量数据库封装
更简单、更可靠的向量数据库，不需要额外配置
"""

import os
import json
import sys
import numpy as np
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from pathlib import Path

# 添加上级目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from embeddings.bge_local_server import get_bge_embedding

# 加载环境变量
load_dotenv()

# 配置
DB_DIR = os.path.join(os.path.dirname(__file__), "faiss_db")
TOP_K = int(os.getenv("TOP_K", "5"))
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

# 集合名称
COLLECTION_NAMES = {
    "device": "device_kb",
    "song": "song_kb",
    "sales": "sales_kb"
}


class FAISSVectorDB:
    def __init__(self, db_dir: Optional[str] = None):
        self.db_dir = db_dir or DB_DIR
        self.embedding_model = get_bge_embedding()
        
        # 存储所有集合 - 使用简单的字典，不用自定义类了
        self.collections: Dict[str, List[Dict]] = {}
        
        # 加载已保存的数据库
        self._load_collections()
    
    def _get_collection_path(self, collection_name: str) -> str:
        """获取集合的文件路径"""
        return os.path.join(self.db_dir, f"{collection_name}.json")
    
    def _load_collections(self):
        """加载所有集合"""
        Path(self.db_dir).mkdir(parents=True, exist_ok=True)
        
        for name in COLLECTION_NAMES.values():
            filepath = self._get_collection_path(name)
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        self.collections[name] = json.load(f)
                except:
                    self.collections[name] = []
            else:
                self.collections[name] = []
    
    def _save_collection(self, collection_name: str):
        """保存集合到文件"""
        filepath = self._get_collection_path(collection_name)
        # 把 numpy 数组转成列表
        save_data = []
        for doc in self.collections[collection_name]:
            new_doc = doc.copy()
            # 确保 vector 是列表
            vec = new_doc.get('vector')
            if isinstance(vec, np.ndarray):
                new_doc['vector'] = vec.tolist()
            elif not isinstance(vec, list):
                new_doc['vector'] = list(vec)
            save_data.append(new_doc)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)

    def insert_data(self, collection_name: str, data_list: List[Dict[str, Any]]):
        """
        插入数据到集合
        """
        if collection_name not in self.collections:
            self.collections[collection_name] = []
        
        # 获取向量
        texts = [item["text"] for item in data_list]
        embeddings = self.embedding_model.encode_batch(texts)
        
        # 创建文档 - 使用纯字典
        for item, emb in zip(data_list, embeddings):
            doc = {
                "id": item["id"],
                "text": item["text"],
                "metadata": item.get("metadata", {}),
                "vector": emb
            }
            self.collections[collection_name].append(doc)
        
        # 保存
        self._save_collection(collection_name)
        print(f"Inserted {len(data_list)} records into '{collection_name}'")
    
    def search(self, collection_name: str, query: str, top_k: int = TOP_K) -> List[Dict[str, Any]]:
        """
        搜索向量
        """
        if collection_name not in self.collections or len(self.collections[collection_name]) == 0:
            return []
        
        # 获取查询向量
        query_vector = np.array(self.embedding_model.encode(query), dtype=np.float32)
        
        # 计算相似度
        docs = self.collections[collection_name]
        similarities = []
        
        for doc in docs:
            vec = np.array(doc['vector'], dtype=np.float32)
            # 计算余弦相似度
            dot_product = np.dot(query_vector, vec)
            norm1 = np.linalg.norm(query_vector)
            norm2 = np.linalg.norm(vec)
            similarity = dot_product / (norm1 * norm2) if (norm1 * norm2) > 0 else 0
            similarities.append((doc, similarity))
        
        # 排序，取 top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_docs = similarities[:top_k]
        
        # 格式化结果
        results = []
        for doc, score in top_docs:
            results.append({
                "id": doc['id'],
                "text": doc['text'],
                "metadata": doc['metadata'],
                "score": float(score)
            })
        
        return results
    
    def build_from_json(self):
        """从 JSON 文件构建所有知识库"""
        global DATA_DIR
        DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        
        # 构建设备知识库
        device_path = os.path.join(DATA_DIR, "device_manual.json")
        if os.path.exists(device_path):
            with open(device_path, "r", encoding="utf-8") as f:
                device_data = json.load(f)
            
            device_list = []
            for item in device_data:
                device_list.append({
                    "id": item["id"],
                    "text": item["content"],
                    "metadata": {
                        "device_type": item["device_type"],
                        "category": item["category"]
                    }
                })
            
            self.insert_data(COLLECTION_NAMES["device"], device_list)
        
        # 构建歌曲知识库
        song_path = os.path.join(DATA_DIR, "songs.json")
        if os.path.exists(song_path):
            with open(song_path, "r", encoding="utf-8") as f:
                song_data = json.load(f)
            
            song_list = []
            for item in song_data:
                text = (
                    f"歌曲: {item['title']}\n"
                    f"歌手: {item['artist']}\n"
                    f"语种: {item['language']}\n"
                    f"风格: {item['genre']}\n"
                    f"情绪: {', '.join(item['mood'])}\n"
                    f"场景: {', '.join(item['occasion'])}\n"
                    f"难度: {item['difficulty']}\n"
                    f"练习标签: {', '.join(item['practice_tags'])}\n"
                    f"描述: {item['description']}"
                )
                song_list.append({
                    "id": item["id"],
                    "text": text,
                    "metadata": {
                        "title": item["title"],
                        "artist": item["artist"],
                        "genre": item["genre"],
                        "difficulty": item["difficulty"],
                        "occasion": item["occasion"]
                    }
                })
            
            self.insert_data(COLLECTION_NAMES["song"], song_list)
        
        # 构建销售知识库
        sales_path = os.path.join(DATA_DIR, "sales_channel.json")
        if os.path.exists(sales_path):
            with open(sales_path, "r", encoding="utf-8") as f:
                sales_data = json.load(f)
            
            sales_list = []
            for item in sales_data:
                sales_list.append({
                    "id": item["id"],
                    "text": item["content"],
                    "metadata": {
                        "category": item["category"]
                    }
                })
            
            self.insert_data(COLLECTION_NAMES["sales"], sales_list)
    
    def clear_all(self):
        """清空所有集合"""
        for name in COLLECTION_NAMES.values():
            self.collections[name] = []
            filepath = self._get_collection_path(name)
            if os.path.exists(filepath):
                os.remove(filepath)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="FAISS Vector Database Manager")
    parser.add_argument("--build", action="store_true", help="Build the vector database from JSON files")
    parser.add_argument("--clear", action="store_true", help="Clear all collections")
    parser.add_argument("--test", action="store_true", help="Test the database with sample queries")
    
    args = parser.parse_args()
    
    db = FAISSVectorDB()
    
    if args.clear:
        db.clear_all()
    
    if args.build:
        db.build_from_json()
    
    if args.test:
        print("\n=== 测试搜索 ===")
        
        # 测试设备搜索
        print("\n1. 设备搜索: '金运机顶盒黑屏'")
        results = db.search(COLLECTION_NAMES["device"], "金运机顶盒黑屏")
        for i, res in enumerate(results, 1):
            print(f"\n结果 {i} (分数: {res['score']:.4f}):")
            print(res['text'][:200] + "...")
        
        # 测试歌曲搜索
        print("\n2. 歌曲搜索: '适合老人小孩唱的歌'")
        results = db.search(COLLECTION_NAMES["song"], "适合老人小孩唱的歌")
        for i, res in enumerate(results, 1):
            print(f"\n结果 {i} (分数: {res['score']:.4f}):")
            print(res['text'][:200] + "...")
        
        # 测试销售搜索
        print("\n3. 销售搜索: '华东区Q1出货'")
        results = db.search(COLLECTION_NAMES["sales"], "华东区Q1出货")
        for i, res in enumerate(results, 1):
            print(f"\n结果 {i} (分数: {res['score']:.4f}):")
            print(res['text'][:200] + "...")


if __name__ == "__main__":
    main()

