"""
雷石 K 歌智能助手 - Python 启动脚本
替代 PowerShell 脚本，跨平台兼容
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def print_banner():
    print("\n" + "="*80)
    print("🎤 雷石 K 歌智能助手".center(80))
    print("="*80 + "\n")

def check_python():
    print("1. 检查 Python 环境...", end="")
    try:
        version = sys.version_info
        print(f" ✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    except Exception as e:
        print(f" ✗ 失败: {e}")
        return False

def check_env_file():
    print("2. 检查配置文件...", end="")
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if not env_file.exists():
        if env_example.exists():
            import shutil
            shutil.copy(env_example, env_file)
            print(" ✓ 已从 .env.example 创建 .env")
            print("\n⚠ 请编辑 .env 文件，填写您的 ZHIPUAI_API_KEY")
            print("获取 API Key: https://open.bigmodel.cn/")
            choice = input("\n是否继续？(Y/N): ").strip().upper()
            if choice != "Y":
                return False
        else:
            print(" ✗ 未找到 .env.example 文件")
            return False
    else:
        print(" ✓ 找到 .env 文件")
    
    # 检查是否有 API Key
    with open(env_file, "r", encoding="utf-8") as f:
        content = f.read()
        if "your_zhipu_api_key_here" in content:
            print("\n⚠ 检测到 API Key 未配置！")
            api_key = input("请输入您的 ZHIPUAI_API_KEY: ").strip()
            content = content.replace("your_zhipu_api_key_here", api_key)
            with open(env_file, "w", encoding="utf-8") as f:
                f.write(content)
            print(" ✓ API Key 已保存到 .env 文件")
    
    return True

def check_dependencies():
    print("3. 检查依赖...", end="")
    try:
        import streamlit
        import numpy
        import sentence_transformers
        print(" ✓ 依赖已安装")
        return True
    except ImportError:
        print("\n正在安装依赖...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print(" ✓ 依赖安装成功")
            return True
        except subprocess.CalledProcessError:
            print(" ✗ 依赖安装失败，请手动运行: pip install -r requirements.txt")
            return False

def check_vector_db():
    print("4. 检查向量数据库...", end="")
    db_path = Path("vector_db/faiss_db")
    if not db_path.exists() or len(list(db_path.glob("*.json"))) == 0:
        print("\n向量数据库不存在，正在构建...")
        print("(首次运行需要下载 BGE 模型，可能需要几分钟)")
        try:
            subprocess.check_call([sys.executable, "vector_db/faiss_db.py", "--build"])
            print(" ✓ 向量数据库构建成功")
            return True
        except subprocess.CalledProcessError:
            print(" ✗ 向量数据库构建失败")
            return False
    else:
        print(" ✓ 向量数据库已存在")
        return True

def start_app():
    print("\n5. 启动应用...")
    print("\n🎉 应用即将启动！")
    print("浏览器将自动打开 http://localhost:8501")
    print("按 Ctrl+C 停止服务\n")
    print("="*80 + "\n")
    time.sleep(2)
    
    try:
        subprocess.check_call([sys.executable, "-m", "streamlit", "run", "web/app.py"])
    except KeyboardInterrupt:
        print("\n\n应用已停止")

def main():
    print_banner()
    
    if not check_python():
        return
    if not check_env_file():
        return
    if not check_dependencies():
        return
    if not check_vector_db():
        return
    
    start_app()

if __name__ == "__main__":
    main()
