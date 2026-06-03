
"""
Streamlit 前端界面
支持文本对话和图片输入
"""

import os
import sys
import base64
from io import BytesIO
from PIL import Image
import streamlit as st

# 添加上级目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.agent_loop import get_karaoke_agent
from zhipuai import ZhipuAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 初始化智谱 AI 客户端（用于图片分析）
ZHIPU_API_KEY = os.getenv("ZHIPUAI_API_KEY")
zhipu_client = ZhipuAI(api_key=ZHIPU_API_KEY)

# 设置页面配置
st.set_page_config(
    page_title="雷石 K 歌智能助手",
    page_icon="🎤",
    layout="wide"
)

# 初始化会话状态
if "agent" not in st.session_state:
    st.session_state.agent = get_karaoke_agent()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None


def image_to_base64(image: Image.Image) -> str:
    """将图片转换为 base64 编码"""
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()


def analyze_image(image: Image.Image, user_text: str = "") -> str:
    """使用智谱 AI 分析图片"""
    try:
        base64_image = image_to_base64(image)
        
        prompt = """你是一个专业的设备故障分析专家。请分析这张图片，判断可能是什么设备问题。
        图片内容可能是：
        - 设备故障提示
        - 错误代码
        - 设备状态显示
        - 接线问题
        请用简洁的语言描述图片中的问题，不要超过100字。
        如果用户有额外的文字描述，请结合起来分析。
        """
        
        if user_text:
            prompt += f"\n用户补充描述: {user_text}"
        
        response = zhipu_client.chat.completions.create(
            model="GLM-4V-Flash",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"图片分析失败: {str(e)}"


# 页面标题
st.title("🎤 雷石 K 歌智能助手")
st.markdown("---")

# 侧边栏
with st.sidebar:
    st.header("功能说明")
    st.markdown("""
    ### 支持的功能
    1. **设备帮助** - 智能电视、机顶盒、音响等设备问题
    2. **智能选歌** - 根据场景推荐合适的歌曲
    3. **销售分析** - 渠道、出货、竞品等业务查询
    4. **图片问诊** - 上传设备故障图片咨询
    
    ### 使用提示
    - 可以同时询问多个问题
    - 支持上传设备故障图片
    - 对话支持多轮上下文
    """)
    
    if st.button("清空对话"):
        st.session_state.agent.reset_conversation()
        st.session_state.messages = []
        st.session_state.uploaded_image = None
        st.rerun()
    
    st.markdown("---")
    st.header("快捷问题")
    quick_questions = [
        "我的金运机顶盒黑屏了怎么办？",
        "推荐几首适合家庭聚会的歌",
        "华东区Q1智能音响出货量怎么样？",
        "主要竞品有哪些？"
    ]
    for q in quick_questions:
        if st.button(q, use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": q})
            with st.spinner("正在思考..."):
                response = st.session_state.agent.chat(q)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

# 主对话区域
st.subheader("对话")

# 显示历史消息
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if "image" in message:
            st.image(message["image"], caption="用户上传的图片")
        st.markdown(message["content"])

# 图片上传区域
uploaded_file = st.file_uploader(
    "上传设备故障图片（可选）",
    type=["jpg", "jpeg", "png"],
    key="image_uploader"
)

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.session_state.uploaded_image = image
    st.image(image, caption="已上传图片", width=300)

# 输入区域
if prompt := st.chat_input("请输入您的问题..."):
    # 添加用户消息
    user_message = {"role": "user", "content": prompt}
    if st.session_state.uploaded_image:
        user_message["image"] = st.session_state.uploaded_image
    
    st.session_state.messages.append(user_message)
    
    with st.chat_message("user"):
        if st.session_state.uploaded_image:
            st.image(st.session_state.uploaded_image, caption="您上传的图片")
        st.markdown(prompt)
    
    # 处理图片和文本
    combined_query = prompt
    if st.session_state.uploaded_image:
        with st.spinner("正在分析图片..."):
            image_analysis = analyze_image(st.session_state.uploaded_image, prompt)
            combined_query = f"{prompt}\n\n图片分析: {image_analysis}"
            st.info(f"图片分析结果: {image_analysis}")
    
    # 调用 Agent
    with st.chat_message("assistant"):
        with st.spinner("正在思考..."):
            response = st.session_state.agent.chat(combined_query)
        st.markdown(response)
    
    # 添加助手响应
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # 清空上传图片
    st.session_state.uploaded_image = None

# 页脚
st.markdown("---")
st.markdown("© 2024 雷石 K 歌智能助手 - 让 K 歌更简单")
