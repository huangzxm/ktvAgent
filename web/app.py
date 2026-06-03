"""
雷石 K 歌智能助手 - 简洁清晰风格
"""

import os
import sys
import base64
from io import BytesIO
from PIL import Image
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.agent_loop import get_karaoke_agent
from zhipuai import ZhipuAI
from dotenv import load_dotenv

load_dotenv()

ZHIPU_API_KEY = os.getenv("ZHIPUAI_API_KEY")
zhipu_client = ZhipuAI(api_key=ZHIPU_API_KEY)

st.set_page_config(
    page_title="雷石 K 歌智能助手",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .stApp {
        background-color: #ffffff !important;
    }
    
    /* 顶部橙色导航栏 */
    .top-nav {
        background: linear-gradient(90deg, #f7931e, #ff7e00);
        padding: 0.8rem 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
    }
    
    .nav-logo {
        display: flex;
        align-items: center;
        gap: 0.8rem;
    }
    
    .nav-logo-text {
        color: white;
        font-size: 1.3rem;
        font-weight: 700;
    }
    
    /* 标题区域 */
    .hero-title {
        color: #333333;
        font-size: 1.8rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.3rem;
    }
    
    .hero-subtitle {
        color: #666666;
        text-align: center;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    
    /* 功能卡片 */
    .feature-card {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1.5rem 1rem;
        text-align: center;
        transition: all 0.3s;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    
    .feature-card:hover {
        border-color: #f7931e;
        box-shadow: 0 4px 15px rgba(247,147,30,0.15);
        transform: translateY(-2px);
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 0.8rem;
    }
    
    .feature-title {
        color: #333333;
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 0.4rem;
    }
    
    .feature-desc {
        color: #666666;
        font-size: 0.9rem;
    }
    
    /* 快捷按钮 */
    .quick-section {
        background: #f8f8f8;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 2rem 0;
    }
    
    .quick-title {
        color: #333333;
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    /* 聊天区域 */
    .chat-container {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1.5rem;
    }
    
    .chat-header {
        color: #333333;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #eee;
    }
    
    /* 页脚 */
    .footer {
        text-align: center;
        margin-top: 3rem;
        color: #999;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)


def image_to_base64(image: Image.Image) -> str:
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()


def analyze_image(image: Image.Image, user_text: str = "") -> str:
    try:
        base64_image = image_to_base64(image)
        prompt = """你是一个专业的设备故障分析专家。请分析这张图片，判断可能是什么设备问题。
        图片内容可能是：设备故障提示、错误代码、设备状态显示、接线问题。
        请用简洁的语言描述图片中的问题，不要超过100字。如果用户有额外的文字描述，请结合起来分析。
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
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        }
                    ]
                }
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"图片分析失败: {str(e)}"


def main():
    if "agent" not in st.session_state:
        st.session_state.agent = get_karaoke_agent()
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "uploaded_image" not in st.session_state:
        st.session_state.uploaded_image = None

    # 顶部橙色导航栏
    st.markdown("""
    <div class="top-nav">
        <div class="nav-logo">
            <span style="font-size:1.5rem;">🎤</span>
            <span class="nav-logo-text">雷石 K 歌智能助手</span>
        </div>
        <div style="color:white; font-size:0.9rem;">专业 K 歌设备服务平台</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 主内容区，居中布局
    container = st.container()
    with container:
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            st.markdown('<h1 class="hero-title">雷石 K 歌智能助手</h1>', unsafe_allow_html=True)
            st.markdown('<p class="hero-subtitle">您的专业 K 歌设备服务平台</p>', unsafe_allow_html=True)
            
            # Tab 栏
            tab1, tab2, tab3 = st.tabs(["💬 智能聊天", "📖 使用帮助", "🔧 关于我们"])
            
            with tab1:
                # 功能卡片
                st.markdown('<div style="margin-bottom:1.5rem;">', unsafe_allow_html=True)
                fcol1, fcol2, fcol3, fcol4 = st.columns(4)
                with fcol1:
                    st.markdown("""
                    <div class="feature-card">
                        <div class="feature-icon">📺</div>
                        <div class="feature-title">设备帮助</div>
                        <div class="feature-desc">安装、故障排查</div>
                    </div>
                    """, unsafe_allow_html=True)
                with fcol2:
                    st.markdown("""
                    <div class="feature-card">
                        <div class="feature-icon">🎵</div>
                        <div class="feature-title">智能选歌</div>
                        <div class="feature-desc">场景、难度推荐</div>
                    </div>
                    """, unsafe_allow_html=True)
                with fcol3:
                    st.markdown("""
                    <div class="feature-card">
                        <div class="feature-icon">📊</div>
                        <div class="feature-title">业务分析</div>
                        <div class="feature-desc">销售、竞品分析</div>
                    </div>
                    """, unsafe_allow_html=True)
                with fcol4:
                    st.markdown("""
                    <div class="feature-card">
                        <div class="feature-icon">🖼️</div>
                        <div class="feature-title">图片问诊</div>
                        <div class="feature-desc">上传故障图片</div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # 快捷问题
                st.markdown('<div class="quick-section">', unsafe_allow_html=True)
                st.markdown('<div class="quick-title">🔥 热门问题</div>', unsafe_allow_html=True)
                q1, q2, q3, q4 = st.columns(4)
                quick_questions = [
                    ("机顶盒黑屏了怎么办？", "我的机顶盒黑屏了怎么办？"),
                    ("推荐家庭聚会歌曲", "推荐一些适合家庭聚会的歌曲"),
                    ("华东区Q1出货情况", "华东区Q1智能音响出货情况怎么样？"),
                    ("主要竞品优劣势", "主要竞品有哪些优劣势？")
                ]
                for idx, (btn_text, question_text) in enumerate(quick_questions):
                    col = [q1, q2, q3, q4][idx]
                    if col.button(btn_text, key=f"q_{idx}", use_container_width=True):
                        st.session_state.messages.append({"role": "user", "content": question_text})
                        with st.spinner("正在处理中..."):
                            response = st.session_state.agent.chat(question_text)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
                
                # 聊天区域
                st.markdown('<div class="chat-container">', unsafe_allow_html=True)
                st.markdown('<div class="chat-header">💬 智能对话</div>', unsafe_allow_html=True)
                
                # 上传图片
                uploaded_file = st.file_uploader(
                    "📷 上传设备故障图片（可选）",
                    type=["jpg", "jpeg", "png"],
                    key="image_uploader"
                )
                if uploaded_file is not None:
                    image = Image.open(uploaded_file)
                    st.session_state.uploaded_image = image
                    st.image(image, caption="已上传的图片", width=280)
                
                # 聊天历史
                for message in st.session_state.messages:
                    with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🤖"):
                        if "image" in message:
                            st.image(message["image"], caption="用户上传的图片", width=280)
                        st.markdown(message["content"])
                
                # 输入区域
                if prompt := st.chat_input("请输入您的问题..."):
                    user_message = {"role": "user", "content": prompt}
                    if st.session_state.uploaded_image:
                        user_message["image"] = st.session_state.uploaded_image
                    st.session_state.messages.append(user_message)
                    
                    with st.chat_message("user", avatar="👤"):
                        if st.session_state.uploaded_image:
                            st.image(st.session_state.uploaded_image, caption="您上传的图片", width=280)
                        st.markdown(prompt)
                    
                    combined_query = prompt
                    if st.session_state.uploaded_image:
                        with st.spinner("正在分析图片..."):
                            image_analysis = analyze_image(st.session_state.uploaded_image, prompt)
                            combined_query = f"{prompt}\n\n图片分析结果: {image_analysis}"
                            st.info(f"图片分析: {image_analysis}")
                    
                    with st.chat_message("assistant", avatar="🤖"):
                        with st.spinner("正在处理中..."):
                            response = st.session_state.agent.chat(combined_query)
                        st.markdown(response)
                    
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.session_state.uploaded_image = None
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            with tab2:
                st.markdown("""
                <div style="background:#f8f8f8; border-radius:8px; padding:2rem;">
                    <h2 style="color:#333; font-size:1.4rem; margin-bottom:1.5rem;">📖 使用帮助</h2>
                    
                    <h3 style="color:#f7931e; font-size:1.1rem; margin-top:1.5rem;">📺 设备使用帮助</h3>
                    <p style="color:#666; line-height:1.8;">支持智能电视、机顶盒、智能音响、鸿蒙智慧屏等设备的安装配置、故障排查、功能使用说明。</p>
                    
                    <h3 style="color:#f7931e; font-size:1.1rem; margin-top:1.5rem;">🎵 智能选歌与练唱</h3>
                    <p style="color:#666; line-height:1.8;">根据场合、难度、风格等条件推荐歌曲，或获取练唱建议。支持标签：家庭聚会、老人/孩子、练气息、高音练习等。</p>
                    
                    <h3 style="color:#f7931e; font-size:1.1rem; margin-top:1.5rem;">📊 业务数据分析</h3>
                    <p style="color:#666; line-height:1.8;">查询各区域出货数据、渠道商表现、竞品分析等业务信息。</p>
                    
                    <h3 style="color:#f7931e; font-size:1.1rem; margin-top:1.5rem;">🖼️ 图片问诊</h3>
                    <p style="color:#666; line-height:1.8;">上传设备故障截图，系统会先分析图片内容，再结合知识库给出建议。</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("清空对话历史", key="clear_tab2"):
                    st.session_state.agent.reset_conversation()
                    st.session_state.messages = []
                    st.session_state.uploaded_image = None
                    st.success("对话历史已清空")
            
            with tab3:
                st.markdown("""
                <div style="background:#fff5e6; border-radius:8px; padding:2rem;">
                    <h2 style="color:#333; font-size:1.4rem; margin-bottom:1.5rem;">🔧 关于我们</h2>
                    
                    <div style="margin-bottom:1.5rem;">
                        <h3 style="color:#f7931e; font-size:1.2rem; margin-bottom:0.8rem;">🎤 雷石 K 歌智能助手</h3>
                        <p style="color:#666; line-height:1.8;">
                            雷石是国内 KTV 点歌系统市场份额第一的公司，本智能助手为家用 K 歌设备生态提供：
                        </p>
                        <ul style="color:#666; line-height:2; margin-left:1.5rem;">
                            <li>C 端消费者设备使用帮助与选歌推荐</li>
                            <li>B 端渠道销售数据分析支持</li>
                            <li>多模态设备故障问诊</li>
                        </ul>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # 页脚
            st.markdown("""
            <div class="footer">
                <p>© 2024 雷石 K 歌智能助手 | 专业 K 歌设备服务平台</p>
            </div>
            """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
