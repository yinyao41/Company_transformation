# -*- coding: utf-8 -*-
import streamlit as st
import requests
from docx import Document
from io import BytesIO
from openai import OpenAI
import os

# =============================================================================
# 配置区（请根据实际情况修改仓库信息）
# =============================================================================
GITHUB_USERNAME = "yinyao41"  # 替换为你的 GitHub 用户名
GITHUB_REPO = "Company_transformation"  # 假设的仓库名，根据实际创建
BRANCH = "master"  # 你的默认分支

# 模板文件的精确路径（假设上传到 data/ 文件夹，根据实际调整）
TEMPLATE_FILES = [
    "data/山东固丰体育产业有限公司转型升级分析报告.docx",
    "data/转型升级方案（六套）2026.03.docx",
]

# 系统提示词（指导 AI 生成转型升级方案）
SYSTEM_PROMPT = """你是一位专业的公司转型升级咨询专家。
基于提供的模板报告和方案，结合用户输入的公司信息，生成一份针对该公司的转型升级分析报告和方案。
报告结构包括：公司背景分析、当前问题、转型升级路径（至少3-5套方案）、实施建议、预期效果。
必须严格参考模板内容，不得编造信息。输出格式为 Markdown，便于阅读。"""

# =============================================================================
# 阿里通义千问客户端
# =============================================================================
DASHSCOPE_API_KEY = st.secrets.get("DASHSCOPE_API_KEY", os.getenv("DASHSCOPE_API_KEY"))

if not DASHSCOPE_API_KEY:
    st.error("缺少 DASHSCOPE_API_KEY！请在 Streamlit Cloud → Settings → Secrets 中添加")
    st.stop()

client = OpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

MODEL_NAME = "qwen-max"

# =============================================================================
# 从 GitHub 下载并解析模板文件
# =============================================================================
@st.cache_data(show_spinner="正在从 GitHub 下载并解析模板文件...")
def load_templates():
    templates = []
    for rel_path in TEMPLATE_FILES:
        raw_url = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{GITHUB_REPO}/{BRANCH}/{rel_path}"
        
        try:
            r = requests.get(raw_url, timeout=15)
            r.raise_for_status()
            
            doc = Document(BytesIO(r.content))
            text = "\n".join(p.text.strip() for p in doc.paragraphs if p.text.strip())
            
            if text:
                display_name = rel_path.split("/")[-1].replace(".docx", "")
                templates.append(f"【{display_name}】\n{text}\n{'─' * 80}\n")
            else:
                st.warning(f"模板文件为空：{rel_path}")
        except Exception as e:
            st.error(f"读取失败 {rel_path}：{str(e)}")
            continue

    if not templates:
        st.error("模板文件加载失败！请确认已上传到 GitHub。")
        st.stop()

    full_text = "".join(templates)
    
    # 自动截断防超限
    MAX_CHARS = 25000
    if len(full_text) > MAX_CHARS:
        full_text = full_text[:MAX_CHARS] + "\n\n【注意：模板全文已自动截断】"
    
    return full_text

# 执行加载
TEMPLATES_TEXT = load_templates()

# =============================================================================
# Streamlit 界面（极简设计：只剩主标题 + 输入区 + 输出）
# =============================================================================
st.set_page_config(page_title="公司转型升级方案生成器", layout="wide")
st.title("🏭 公司转型升级方案生成器")

# 用户输入区
with st.form(key="company_info_form"):
    company_name = st.text_input("公司名称", placeholder="例如：山东固丰体育产业有限公司")
    industry = st.text_input("所属行业", placeholder="例如：体育产业")
    current_status = st.text_area("公司当前情况描述", placeholder="描述公司规模、问题、优势等（可选）")
    additional_info = st.file_uploader("上传公司相关文件（可选，支持 PDF/DOCX/TXT）", type=["pdf", "docx", "txt"])
    
    submit_button = st.form_submit_button(label="生成转型升级方案")

if submit_button:
    if not company_name or not industry:
        st.error("请至少输入公司名称和所属行业！")
    else:
        # 处理上传文件（如果有）
        extra_text = ""
        if additional_info:
            if additional_info.type == "application/pdf":
                st.warning("PDF 处理暂不支持，请上传 DOCX 或 TXT。")
            elif additional_info.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                doc = Document(BytesIO(additional_info.read()))
                extra_text = "\n".join(p.text.strip() for p in doc.paragraphs if p.text.strip())
            else:  # TXT
                extra_text = additional_info.read().decode("utf-8")
        
        # 构建用户输入上下文
        user_context = f"公司名称：{company_name}\n行业：{industry}\n当前情况：{current_status}\n附加信息：{extra_text}"
        
        # 生成方案
        with st.spinner("正在调用 AI 生成方案..."):
            try:
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT + "\n\n模板内容：\n" + TEMPLATES_TEXT},
                        {"role": "user", "content": f"基于模板，为以下公司生成转型升级方案：\n{user_context}"}
                    ],
                    temperature=0.3,
                    max_tokens=3000,
                )
                
                scheme = response.choices[0].message.content
                st.markdown("### 生成的转型升级方案")
                st.markdown(scheme)
                
            except Exception as e:
                st.error(f"AI 调用失败：{str(e)}")
