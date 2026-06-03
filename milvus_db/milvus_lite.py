
"""
Milvus Lite 向量数据库封装
用于构建和查询设备、歌曲、销售三个知识库
"""

import os
import json
import sys
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# 添加上级目录到路径，以便导入 embeddings 模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from embeddings.bge_local_server import get_bge_embedding
from pymilvus import MilvusClient, connections, utility
from pymilvus import CollectionSchema, FieldSchema, DataType

# 加载环境变量
load_dotenv()

# 配置
MILVUS_DB_PATH = os.getenv("MILVUS_DB_PATH", os.path.join(os.path.dirname(__file__), "milvus_demo.db"))
TOP_K = int(os.getenv("TOP_K", "5"))
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

# 集合名称
COLLECTION_NAMES = {
    "device": "device_manual",
    "song": "song_knowledge",
    "sales": "sales_data"
}


class MilvusVectorDB:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or MILVUS_DB_PATH
        self.client = MilvusClient(self.db_path)
        self.embedding_model = get_bge_embedding()
        self._ensure_collections()

    def _ensure_collections(self):
        """确保所有集合存在"""
        for name in COLLECTION_NAMES.values():
            if not self.client.has_collection(collection_name=name):
                self._create_collection(name)

    def _create_collection(self, collection_name: str):
        """创建向量集合"""
        dimension = self.embedding_model.get_dimension()
        
        fields = [
            FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=50, is_primary=True, auto_id=False),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=4096),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=dimension),
            FieldSchema(name="metadata", dtype=DataType.JSON)
        ]
        
        schema = CollectionSchema(fields=fields, description=f"{collection_name} knowledge base")
        
        index_params = self.client.prepare_index_params()
        index_params.add_index(
            field_name="vector",
            index_type="IVF_FLAT",
            metric_type="COSINE",
            params={"nlist": 128}
        )
        
        self.client.create_collection(
            collection_name=collection_name,
            schema=schema,
            index_params=index_params
        )
        
        print(f"Collection '{collection_name}' created successfully")

    def insert_data(self, collection_name: str, data_list: List[Dict[str, Any]]):
        """
        插入数据到集合
        :param collection_name: 集合名称
        :param data_list: 数据列表，每个元素包含 id, text, metadata
        """
        # 准备数据
        texts = [item["text"] for item in data_list]
        embeddings = self.embedding_model.encode_batch(texts)
        
        insert_data = []
        for item, emb in zip(data_list, embeddings):
            insert_data.append({
                "id": item["id"],
                "text": item["text"],
                "vector": emb,
                "metadata": item.get("metadata", {})
            })
        
        self.client.insert(collection_name=collection_name, data=insert_data)
        print(f"Inserted {len(insert_data)} records into '{collection_name}'")

    def search(self, collection_name: str, query: str, top_k: int = TOP_K) -> List[Dict[str, Any]]:
        """
        搜索向量
        :param collection_name: 集合名称
        :param query: 查询文本
        :param top_k: 返回结果数量
        :return: 搜索结果列表，包含 id, text, metadata, score
        """
        query_embedding = self.embedding_model.encode(query)
        
        search_params = {"metric_type": "COSINE", "params": {"nprobe": 10}}
        
        results = self.client.search(
            collection_name=collection_name,
            data=[query_embedding],
            limit=top_k,
            search_params=search_params,
            output_fields=["id", "text", "metadata"]
        )
        
        formatted_results = []
        for hit in results[0]:
            formatted_results.append({
                "id": hit["id"],
                "text": hit["entity"]["text"],
                "metadata": hit["entity"]["metadata"],
                "score": hit["distance"]
            })
        
        return formatted_results

    def build_from_json(self):
        """从 JSON 文件构建所有知识库"""
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
            if self.client.has_collection(collection_name=name):
                self.client.drop_collection(collection_name=name)
                print(f"Dropped collection '{name}'")
        self._ensure_collections()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Milvus Vector Database Manager")
    parser.add_argument("--build", action="store_true", help="Build the vector database from JSON files")
    parser.add_argument("--clear", action="store_true", help="Clear all collections")
    parser.add_argument("--test", action="store_true", help="Test the database with sample queries")
    
    args = parser.parse_args()
    
    db = MilvusVectorDB()
    
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
            print(res["text"][:200] + "...")
        
        # 测试歌曲搜索
        print("\n2. 歌曲搜索: '适合老人小孩唱的歌'")
        results = db.search(COLLECTION_NAMES["song"], "适合老人小孩唱的歌")
        for i, res in enumerate(results, 1):
            print(f"\n结果 {i} (分数: {res['score']:.4f}):")
            print(res["text"][:200] + "...")
        
        # 测试销售搜索
        print("\n3. 销售搜索: '华东区Q1出货'")
        results = db.search(COLLECTION_NAMES["sales"], "华东区Q1出货")
        for i, res in enumerate(results, 1):
            print(f"\n结果 {i} (分数: {res['score']:.4f}):")
            print(res["text"][:200] + "...")


if __name__ == "__main__":
    main()
