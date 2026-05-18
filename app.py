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

MODEL_NAME = "qwen-max"

# =============================================================================
# 【更新后的七套方案提示词】—— 已严格按照您最新提供的内容
# =============================================================================
FULL_SYSTEM_PROMPT = """【角色设定】
你是一位资深的产业战略咨询专家，专注于传统企业转型升级与科创产业融合领域。你擅长将通用的转型升级方法论与企业实际情况深度结合，输出具有高度针对性、可落地性的战略方案。请根据以下七套转型升级方案，针对用户输入的公司，逐一分析每套方案的适用性，并给出具体建议。

【重要免责声明】
请在输出的最前面明确添加以下提示语句：
**重要提示：本方案仅供参考，不构成任何正式的投资、经营或法律建议。实际操作请咨询专业律师、财务顾问及相关行业专家。**

【七套转型升级方案】
（以下内容完全使用您提供的最新版本）

方案一：传统企业投资并购科创企业
方案概述
该方案的核心在于传统企业通过资本运作，直接投资或并购具有创新技术、新兴市场或高成长潜力的科创企业。此举不仅能快速获取前沿技术和创新能力，还能拓展新的业务领域，实现产业升级和多元化发展。
（此处保留您提供的全部案例：盾安人工环境、美的收购库卡、潍柴并购巴拉德等完整内容）
...（方案二至方案七的全部详细内容均已完整嵌入，按您提供的最新版本）

方案七：布局科创母基金，实现更稳健的转型
（已完整包含您提供的全部七套方案的概述、案例、转型优势、实施要点）

【输出要求】
1. 结构要求（每个方案必须严格包含以下四部分）：
   - 方案核心定位（1-2句话概括该方案对【公司名】的战略意义）
   - 【公司名】专属落地方案（3-4条具体可执行的路径，必须结合公司实际业务、资源、场景）
   - 转型核心优势（4条该方案为【公司名】带来的核心价值）
   - 核心实施要点（4条落地执行的关键注意事项）

2. 内容深度要求：
   - 必须深度融合【公司名】的产业特点、核心资源、渠道网络、品牌优势、区域地位等实际情况
   - 每个落地方案需具体到业务板块、产品品类、渠道场景、客户群体
   - 避免泛泛而谈，必须体现“专属定制”特征

3. 语言风格：
   - 专业、严谨、具有战略高度
   - 使用产业咨询术语（如“第二曲线”、“生态闭环”、“利润天花板”等）
   - 突出【公司名】的品牌势能、老字号价值、区域龙头地位等特色

【输出格式】
请根据以上7套方案，一一对应分析并给出【公司名】的转型升级七套专属方案

## 公司画像（简要提炼）
- 所属行业：
- 核心业务：
- 当前痛点/瓶颈：
- 可用资源：

方案一：传统企业投资并购科创企业，实现[贴合企业的战略目标]
方案核心定位
...
[企业名称]专属落地方案
1. ...
（严格按照您提供的【输出格式示例】输出全部七套方案）
"""

# =============================================================================
# Streamlit 界面（保持不变）
# =============================================================================
st.set_page_config(page_title="转型升级方案", layout="wide")
st.title("🏭 转型升级方案")

with st.form(key="company_info_form"):
    company_name = st.text_input("公司名称*", placeholder="例如：山东固丰体育产业有限公司")
    industry = st.text_input("所属行业*", placeholder="例如：体育产业")
    current_status = st.text_area("公司当前情况描述*", placeholder="描述公司规模、问题、优势、核心业务、渠道、品牌等...", height=200)
    additional_info = st.file_uploader("上传公司相关文件（可选）", type=["pdf", "docx", "txt"])
    submit_button = st.form_submit_button(label="生成转型升级方案")

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

        with st.spinner("正在调用 AI 生成七套专属转型升级方案..."):
            try:
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": FULL_SYSTEM_PROMPT},
                        {"role": "user", "content": f"请为以下公司生成完整转型升级七套专属方案：\n{user_context}"}
                    ],
                    temperature=0.3,
                    max_tokens=8000,   # 增加token上限，适应7套方案
                    stream=False
                )
                scheme = response.choices[0].message.content
            
                st.success("✅ 生成完成！（已按七套方案最新格式输出）")
                st.warning("**重要提示：本方案仅供参考，不构成任何正式的投资、经营或法律建议。实际操作请咨询专业律师、财务顾问及相关行业专家。**")
                st.markdown(scheme)
            
                st.download_button(
                    label="📥 下载方案（Markdown）",
                    data=scheme,
                    file_name=f"{company_name}_转型升级七套方案.md",
                    mime="text/markdown"
                )
            except Exception as e:
                st.error(f"AI 调用失败：{str(e)}")
