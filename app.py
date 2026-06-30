import streamlit as st
import requests
from docx import Document
from io import BytesIO
from openai import OpenAI
import os

# =============================================================================
# 配置区
# =============================================================================
DASHSCOPE_API_KEY = st.secrets.get("DASHSCOPE_API_KEY", os.getenv("DASHSCOPE_API_KEY"))
if not DASHSCOPE_API_KEY:
    st.error("缺少 DASHSCOPE_API_KEY！请在 Streamlit Secrets 中添加")
    st.stop()

client = OpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

MODEL_NAME = "qwen-plus"  # 推荐使用 plus 更快，必要时改回 qwen-max

# =============================================================================

# =============================================================================
SCHEME_DOC_PATH = "data/附件2-4-1 九套转型升级方向.202605.docx"

FULL_SYSTEM_PROMPT = """【角色设定】
你是一位资深的产业战略咨询专家，专注于传统企业转型升级与科创产业融合领域。

【重要免责声明】
请在输出的最前面明确添加以下提示语句：
**重要提示：本方向仅供参考，不构成任何正式的投资、经营或法律建议。实际操作请咨询专业律师、财务顾问及相关行业专家。**

【九套转型升级方向库】
以下是完整的九套方向内容（已从文档中读取）：
"""

# 自动加载文档内容并拼接到 Prompt
try:
    if os.path.exists(SCHEME_DOC_PATH):
        doc = Document(SCHEME_DOC_PATH)
        doc_text = "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip()])
        FULL_SYSTEM_PROMPT += doc_text
        st.success(" ")
    else:
        FULL_SYSTEM_PROMPT += "（方向文档加载失败，请检查 data 目录）"
except Exception as e:
    FULL_SYSTEM_PROMPT += f"（方向文档加载失败: {str(e)}）"

FULL_SYSTEM_PROMPT += """
【输出要求】
请严格按照以下格式为用户公司生成**九套**专属转型升级方向：
1. 结构要求（每个方向必须包含）：
   - 方向核心定位（1-2句话）
   - [公司名]专属落地方案（3-4条具体路径，结合公司实际）
   - 转型核心优势（4条）
   - 核心实施要点（4条）
2. 必须深度定制，结合公司行业、业务、资源、痛点。
3. 语言专业，使用“第二曲线”、“精益红利”等术语。
"""

# =============================================================================
# Streamlit 界面
# =============================================================================
st.set_page_config(page_title="转型升级方向", layout="wide")
st.title("🏭 企业转型升级方向生成器")
st.caption("✅")

with st.form(key="company_info_form"):
    company_name = st.text_input("公司名称*", placeholder="例如：山东固丰体育产业有限公司")
    industry = st.text_input("所属行业*", placeholder="例如：体育产业")
    current_status = st.text_area("公司当前情况描述*", 
                                  placeholder="描述公司规模、问题、优势、核心业务、渠道、品牌等...", 
                                  height=200)
    additional_info = st.file_uploader("额外上传补充文件（可选）", type=["pdf", "docx", "txt"])
    submit_button = st.form_submit_button(label="生成九套转型升级方向")

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

        with st.spinner("正在生成九套专属方向...（约 30-60 秒）"):
            try:
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": FULL_SYSTEM_PROMPT},
                        {"role": "user", "content": f"请为以下公司生成完整转型升级九套专属方向：\n{user_context}"}
                    ],
                    temperature=0.3,
                    max_tokens=7500,
                    stream=False
                )
                scheme = response.choices[0].message.content

                st.success("✅ 生成完成！")
                st.warning("**重要提示：本方向仅供参考，不构成任何正式的投资、经营或法律建议。**")
                st.markdown(scheme)

                st.download_button(
                    label="📥 下载方案（Markdown）",
                    data=scheme,
                    file_name=f"{company_name}_转型升级九套方向.md",
                    mime="text/markdown"
                )
            except Exception as e:
                st.error(f"AI 调用失败：{str(e)}")
