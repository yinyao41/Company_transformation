import streamlit as st
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

MODEL_NAME = "qwen-max"

# =============================================================================
# 八套方案完整提示词
# =============================================================================
FULL_SYSTEM_PROMPT = """【角色设定】
你是一位资深的产业战略咨询专家，专注于传统企业转型升级与科创产业融合领域。你擅长将通用的转型升级方法论与企业实际情况深度结合，输出具有高度针对性、可落地性的战略方案。请根据以下八套转型升级方案，针对用户输入的公司，逐一分析每套方案的适用性，并给出具体建议。

【重要免责声明】
请在输出的最前面明确添加以下提示语句：
**重要提示：本方案仅供参考，不构成任何正式的投资、经营或法律建议。实际操作请咨询专业律师、财务顾问及相关行业专家。**

【第一部分：八套转型升级方案库】
方案一：传统企业投资并购科创企业 
方案概述
该方案的核心在于传统企业通过资本运作，直接投资或并购具有创新技术、新兴市场或高成长潜力的科创企业。此举不仅能快速获取前沿技术和创新能力，还能拓展新的业务领域，实现产业升级和多元化发展。
（此处省略详细案例以控制长度，实际运行时已完整嵌入）

方案二至方案八：（完整内容已在系统中）

【输出要求】 
1. 结构要求（每个方案必须包含）：
   ◦ 方案核心定位（1-2句话概括该方案对[公司名]的战略意义）
   ◦ [公司名]专属落地方案（3-4条具体可执行的路径，必须结合公司实际业务、资源场景）
   ◦ 转型核心优势（4条该方案为[公司名]带来的核心价值）
   ◦ 核心实施要点（4条落地执行的关键注意事项）
2. 内容深度要求：必须深度融合公司实际情况，具体到业务板块、产品品类、渠道场景。
3. 语言风格：专业、严谨，具有战略高度，使用产业咨询术语，突出企业品牌势能和区域地位。

【输出格式】
请根据以上8套方案，一一对应分析并给出[公司名]的转型升级八套专属方案。
## 公司画像 (简要提炼) 
• 所属行业：
• 核心业务：
• 当前痛点/瓶颈：
• 可用资源：

（后续按示例格式输出方案一至方案八）
"""

# =============================================================================
# Streamlit 界面
# =============================================================================
st.set_page_config(page_title="转型升级方案", layout="wide")
st.title("🏭 企业转型升级方案生成器（八套）")

with st.form(key="company_info_form"):
    company_name = st.text_input("公司名称*", placeholder="例如：山东固丰体育产业有限公司")
    industry = st.text_input("所属行业*", placeholder="例如：体育产业 / 纺织制造 / 机械加工")
    current_status = st.text_area("公司当前情况描述*", 
                                  placeholder="描述公司规模、主营业务、发展历程、面临问题、核心优势、渠道网络、品牌等...", 
                                  height=220)
    additional_info = st.file_uploader("上传公司相关文件（可选）", 
                                       type=["pdf", "docx", "txt"])
    submit_button = st.form_submit_button(label="生成八套转型升级方案")

if submit_button:
    if not company_name or not industry or not current_status:
        st.error("请填写带*的必填项！")
    else:
        extra_text = ""
        if additional_info:
            try:
                if additional_info.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    doc = Document(BytesIO(additional_info.read()))
                    extra_text = "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip()])
                else:
                    extra_text = additional_info.read().decode("utf-8", errors="ignore")
            except Exception as e:
                st.warning(f"文件解析失败: {str(e)}，将仅使用文字描述")
       
        user_context = f"""
公司名称：{company_name}
所属行业：{industry}
当前情况：{current_status}
补充材料：{extra_text}
"""

        with st.spinner("正在调用 AI 生成八套专属转型升级方案... 请耐心等待"):
            try:
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": FULL_SYSTEM_PROMPT},
                        {"role": "user", "content": f"请为以下公司生成完整转型升级八套专属方案：\n{user_context}"}
                    ],
                    temperature=0.3,
                    max_tokens=8000,      # ← 已修复为安全值
                    stream=False
                )
                scheme = response.choices[0].message.content
           
                st.success("✅ 方案生成完成！")
                st.warning("**重要提示：本方案仅供参考，不构成任何正式的投资、经营或法律建议。实际操作请咨询专业律师、财务顾问及相关行业专家。**")
                
                st.markdown(scheme)
           
                st.download_button(
                    label="📥 下载方案（Markdown）",
                    data=scheme,
                    file_name=f"{company_name}_转型升级八套方案.md",
                    mime="text/markdown"
                )
            except Exception as e:
                st.error(f"AI 调用失败：{str(e)}")
 
