
"""
BGE 本地 Embedding 服务
使用 sentence-transformers 库加载 BGE 模型
"""

import os
import numpy as np
from typing import List, Optional
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

# 加载环境变量
load_dotenv()

# 默认模型配置
DEFAULT_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-small-zh-v1.5")
CACHE_DIR = os.path.join(os.path.dirname(__file__), "model_cache")


class BGEEmbedding:
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or DEFAULT_MODEL_NAME
        self.model = None
        self._load_model()

    def _load_model(self):
        """加载 BGE 模型"""
        print(f"正在加载 Embedding 模型: {self.model_name}")
        try:
            self.model = SentenceTransformer(
                self.model_name,
                cache_folder=CACHE_DIR,
                device="cpu"  # 默认使用 CPU，兼容性好
            )
            print("模型加载成功!")
        except Exception as e:
            print(f"模型加载失败: {e}")
            print("尝试下载模型...")
            self.model = SentenceTransformer(
                self.model_name,
                cache_folder=CACHE_DIR,
                device="cpu"
            )
            print("模型加载成功!")

    def encode(self, text: str) -> List[float]:
        """
        编码单个文本为向量
        :param text: 输入文本
        :return: 向量列表
        """
        if self.model is None:
            raise ValueError("模型未加载")
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.tolist()

    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """
        批量编码文本为向量
        :param texts: 文本列表
        :return: 向量列表
        """
        if self.model is None:
            raise ValueError("模型未加载")
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()

    def get_dimension(self) -> int:
        """获取向量维度"""
        if self.model is None:
            raise ValueError("模型未加载")
        return self.model.get_sentence_embedding_dimension()


# 单例模式
_bge_instance = None


def get_bge_embedding() -> BGEEmbedding:
    """获取 BGE Embedding 单例"""
    global _bge_instance
    if _bge_instance is None:
        _bge_instance = BGEEmbedding()
    return _bge_instance


if __name__ == "__main__":
    # 测试代码
    print("=== BGE Embedding 服务测试 ===")
    bge = get_bge_embedding()
    print(f"向量维度: {bge.get_dimension()}")
    
    test_texts = [
        "雷石 K 歌助手",
        "金运机顶盒黑屏问题",
        "智能音响蓝牙连接"
    ]
    
    embeddings = bge.encode_batch(test_texts)
    print(f"\n测试文本编码完成，共 {len(embeddings)} 个向量")
    
    for i, (text, emb) in enumerate(zip(test_texts, embeddings)):
        print(f"\n文本 {i+1}: {text}")
        print(f"向量维度: {len(emb)}")
        print(f"向量前5个值: {emb[:5]}")
