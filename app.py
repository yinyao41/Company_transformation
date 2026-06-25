import streamlit as st
from openai import OpenAI
from docx import Document
from io import BytesIO
import os
import datetime

# =========================
# 页面配置
# =========================
st.set_page_config(
    page_title="企业转型升级方向生成器",
    page_icon="🏭",
    layout="wide"
)

st.title("🏭 企业转型升级方向生成器")
st.markdown("**填写企业信息，自动生成转型升级方向方案**")

# =========================
# API KEY 获取
# =========================
def get_api_key():
    try:
        return st.secrets["QWEN_API_KEY"]
    except:
        pass
    return os.getenv("QWEN_API_KEY")

api_key = get_api_key()

if not api_key:
    st.error("⚠️ 未检测到阿里千问 API Key，请在 Streamlit Secrets 中添加 `QWEN_API_KEY`")
    st.stop()

# =========================
# 企业信息表单
# =========================
with st.form(key="company_info_form"):
    company_name = st.text_input("公司名称*", placeholder="例如：山东固丰体育产业有限公司")
    industry = st.text_input("所属行业*", placeholder="例如：体育产业")
    current_status = st.text_area("公司当前情况描述*",
                                  placeholder="描述公司规模、问题、优势、核心业务、渠道、品牌等...",
                                  height=200)
    additional_info = st.file_uploader("额外上传补充文件（可选）", type=["pdf", "docx", "txt"])
    
    submit_button = st.form_submit_button(label="🚀 生成转型升级方向方案", use_container_width=True)

if submit_button:
    if not company_name or not industry or not current_status:
        st.error("请填写带*的必填项！")
    else:
        extra_text = ""
        if additional_info:
            try:
                if additional_info.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    doc = Document(BytesIO(additional_info.read()))
                    extra_text = "\n".join(p.text.strip() for p in doc.paragraphs if p.text.strip())
                else:
                    extra_text = additional_info.read().decode("utf-8", errors="ignore")
            except:
                st.warning("补充文件解析失败，将使用文字描述")

        user_context = f"""
公司名称：{company_name}
所属行业：{industry}
当前情况：{current_status}
补充材料：{extra_text}
"""

        with st.spinner("正在生成企业转型升级方向方案...（约 30-60 秒）"):
            try:
                client = OpenAI(
                    api_key=api_key,
                    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
                )

                response = client.chat.completions.create(
                    model="qwen-plus",
                    messages=[
                        {"role": "system", "content": "你是一位资深的产业战略咨询专家，专注于传统企业转型升级与科创产业融合领域。"},
                        {"role": "user", "content": f"请为以下公司生成专业转型升级方向方案：\n{user_context}"}
                    ],
                    temperature=0.3,
                    max_tokens=8000
                )

                scheme = response.choices[0].message.content

                st.success("✅ 方案生成完成！")
                st.markdown(scheme)

                # 下载Word
                doc = Document()
                doc.add_heading(f"{company_name} 企业转型升级方向方案", level=1)
                doc.add_paragraph(scheme)
                filename = f"{company_name}_转型升级方向方案_{datetime.date.today()}.docx"
                doc.save(filename)

                with open(filename, "rb") as f:
                    st.download_button(
                        label="📥 下载Word方案",
                        data=f,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )

            except Exception as e:
                st.error(f"生成失败：{str(e)}")

st.caption("Powered by 阿里千问 Qwen")
