
"""
BGE 本地 Embedding 服务
使用 ModelScope 加载模型（国内平台，不用翻墙）
"""

import os
import numpy as np
from typing import List, Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 默认模型配置
DEFAULT_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "Xorbits/bge-small-zh-v1.5")
CACHE_DIR = os.path.join(os.path.dirname(__file__), "model_cache")


class BGEEmbedding:
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or DEFAULT_MODEL_NAME
        self.model = None
        self.tokenizer = None
        self._load_model()

    def _load_model(self):
        """加载 BGE 模型 - 使用 ModelScope"""
        print(f"正在加载 Embedding 模型: {self.model_name}")
        try:
            # 尝试使用 ModelScope
            from modelscope import AutoModel, AutoTokenizer
        except ImportError:
            print("modelscope 未安装，正在安装...")
            import subprocess
            import sys
            subprocess.check_call([sys.executable, "-m", "pip", "install", "modelscope"])
            from modelscope import AutoModel, AutoTokenizer

        try:
            os.makedirs(CACHE_DIR, exist_ok=True)
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name, 
                cache_dir=CACHE_DIR
            )
            self.model = AutoModel.from_pretrained(
                self.model_name, 
                cache_dir=CACHE_DIR
            )
            print("模型加载成功!")
        except Exception as e:
            print(f"从 ModelScope 加载失败: {e}")
            print("\n尝试备用方案...")
            self._load_fallback()

    def _load_fallback(self):
        """备用方案 - 使用简单的 TF-IDF 或其他方法"""
        print("使用备用方案 - 简单的字符级向量...")
        
        # 创建一个简单的 fallback 类
        class FallbackEmbedder:
            def encode(self, texts):
                results = []
                for text in texts:
                    # 简单的字符频率向量
                    vec = np.zeros(512, dtype=np.float32)
                    for i, c in enumerate(text):
                        vec[i % 512] += ord(c)
                    # 归一化
                    norm = np.linalg.norm(vec)
                    if norm > 0:
                        vec = vec / norm
                    results.append(vec)
                return results
        
        self.model = None
        self.fallback = FallbackEmbedder()

    def encode(self, text: str) -> List[float]:
        """
        编码单个文本为向量
        :param text: 输入文本
        :return: 向量列表
        """
        return self.encode_batch([text])[0]

    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """
        批量编码文本为向量
        :param texts: 文本列表
        :return: 向量列表
        """
        if self.model is None:
            # 使用 fallback
            vecs = self.fallback.encode(texts)
            return [vec.tolist() for vec in vecs]
        
        # 使用 BGE 模型
        encoded_input = self.tokenizer(
            texts, 
            padding=True, 
            truncation=True, 
            return_tensors='pt',
            max_length=512
        )
        
        import torch
        with torch.no_grad():
            model_output = self.model(**encoded_input)
            # 使用 <[BOS_never_used_51bce0c785ca2f68081bfa7d91973934]> token 作为文本表示
            sentence_embeddings = model_output[0][:, 0]
        
        # 归一化
        sentence_embeddings = torch.nn.functional.normalize(sentence_embeddings, p=2, dim=1)
        return sentence_embeddings.numpy().tolist()

    def get_dimension(self) -> int:
        """获取向量维度"""
        if self.model is None:
            return 512  # fallback 维度
        # 获取模型维度
        text = "test"
        encoded_input = self.tokenizer(text, return_tensors='pt')
        import torch
        with torch.no_grad():
            output = self.model(**encoded_input)
        return output[0][:, 0].shape[1]


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

