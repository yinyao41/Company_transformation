import streamlit as st
from docx import Document
from io import BytesIO
from openai import OpenAI
import os
import time

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

MODEL_NAME = "qwen-max"

# =============================================================================
# 【大幅精简后的系统提示词】—— 核心优化点
# =============================================================================
FULL_SYSTEM_PROMPT = """你是一位资深的产业战略咨询专家，专注于传统企业转型升级与科创产业融合。
请根据以下八套转型升级方案，为用户提供的公司生成高度定制化的八套专属方案。

【八套方案简要名称与核心要点】
1. 投资并购科创企业：通过资本运作快速获取技术与新赛道。
2. 科创企业带动传统工艺升级：借助科创技术反向提升传统生产精度、材料和利润。
3. 企业数智化转型升级：引入ERP、MES、AI等实现数字化、智能化管理。
4. 传统经销商升级代理高科技高毛利产品。
5. 企业精益管理转型升级：消除浪费、提升效率和盈利能力。
6. 经销商代理高科技产品并成为股东（产融结合）。
7. 成为科创基金管理公司股东或基金投资人。
8. 投资母基金（FoF）实现稳健转型。

【输出要求】
- 输出最前面必须添加：**重要提示：本方案仅供参考，不构成任何正式的投资、经营或法律建议。实际操作请咨询专业顾问。**
- 先输出 ## 公司画像（简要提炼）
- 然后按顺序输出方案一至方案八，每套方案严格包含以下四部分：
  1. 方案核心定位（1-2句话）
  2. [公司名]专属落地方案（3-4条具体路径，结合公司业务、渠道、品牌）
  3. 转型核心优势（4条）
  4. 核心实施要点（4条）
- 语言专业、严谨，突出企业个性化特点，使用“第二曲线”、“精益红利”、“生态闭环”等术语。
- 总输出长度控制在合理范围，避免过于冗长。

请严格按照以上结构输出。"""

# =============================================================================
# Streamlit 界面
# =============================================================================
st.set_page_config(page_title="转型升级方案", layout="wide", page_icon="🏭")
st.title("🏭 企业转型升级方案生成器（八套）")
st.caption("优化版 - 响应更快")

with st.form(key="company_info_form"):
    col1, col2 = st.columns(2)
    with col1:
        company_name = st.text_input("公司名称*", placeholder="山东固丰体育产业有限公司")
        industry = st.text_input("所属行业*", placeholder="体育用品制造")
    with col2:
        company_size = st.text_input("公司规模", placeholder="年营收/员工数")

    current_status = st.text_area("公司当前情况与需求*", 
                                  placeholder="主营业务、核心优势、面临痛点（如利润下滑、渠道老化）、资源（品牌、渠道、网络等）...", 
                                  height=180)
    
    additional_info = st.file_uploader("上传补充材料（可选）", type=["pdf", "docx", "txt"])
    submit_button = st.form_submit_button("🚀 生成八套转型升级方案", type="primary")

if submit_button:
    if not company_name or not industry or not current_status:
        st.error("请填写带*的必填项")
    else:
        extra_text = ""
        if additional_info:
            try:
                if additional_info.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    doc = Document(BytesIO(additional_info.read()))
                    extra_text = "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip()][:500])
                else:
                    extra_text = additional_info.read().decode("utf-8", errors="ignore")[:2000]
            except:
                extra_text = "文件解析失败"

        user_context = f"""
公司名称：{company_name}
所属行业：{industry}
规模：{company_size}
当前情况：{current_status}
补充材料：{extra_text}
"""

        with st.spinner("AI 正在生成方案中，请稍等（通常30-60秒）..."):
            start_time = time.time()
            try:
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": FULL_SYSTEM_PROMPT},
                        {"role": "user", "content": f"请为以下公司生成完整八套转型升级专属方案：\n{user_context}"}
                    ],
                    temperature=0.35,
                    max_tokens=7500,
                    stream=False
                )
                scheme = response.choices[0].message.content
                
                elapsed = round(time.time() - start_time, 1)
                st.success(f"✅ 生成完成！（耗时 {elapsed} 秒）")
                
                st.warning("**重要提示：本方案仅供参考，不构成任何正式的投资、经营或法律建议。**")
                st.markdown(scheme)
                
                st.download_button(
                    label="📥 下载 Markdown 文件",
                    data=scheme,
                    file_name=f"{company_name}_转型升级八套方案.md",
                    mime="text/markdown"
                )
            except Exception as e:
                st.error(f"生成失败：{str(e)}")

st.info("💡 提示：描述越详细，生成的方案针对性越强。")
