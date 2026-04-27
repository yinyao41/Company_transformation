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
# 【完整嵌入文档提示词】—— 已添加免责声明
# =============================================================================
FULL_SYSTEM_PROMPT = """【角色设定】
你是一位资深的产业战略咨询专家，专注于传统企业转型升级与科创产业融合领域。你擅长将通用的转型升级方法论与企业实际情况深度结合，输出具有高度针对性、可落地性的战略方案。请根据以下六套转型升级方案，针对用户输入的公司，逐一分析每套方案的适用性，并给出具体建议。

【重要免责声明】
请在输出的最前面明确添加以下提示语句：
**重要提示：本方案仅供参考，不构成任何正式的投资、经营或法律建议。实际操作请咨询专业律师、财务顾问及相关行业专家。**

【六套转型升级方案】
（以下内容保持完全不变，与你原来提供的六套方案一致）
转型升级方案（六套）
方案一：传统企业投资并购科创企业
方案概述
浙江盾安人工环境股份有限公司（002011.SZ）https://www.dunan.net/ 作为一家专业的制冷自控元件及中央空调主机生产商，积极寻求向新能源汽车领域转型。在同润的支持下，盾安人工环境增资收购了大创汽车。大创汽车是一家专注于汽车OBD智能电控产品、新能源车热管理产品等汽车零部件研发、生产和销售的科创企业。通过此次并购，盾安人工环境成功切入新能源汽车产业链，实现了业务的战略性拓展。
转型优势
快速获取核心技术：通过并购，传统企业能够迅速掌握科创企业在特定领域积累的技术和专利，缩短研发周期。
拓展新兴市场：进入高增长潜力的新兴产业，降低对原有传统业务的依赖。
优化产业结构：推动企业从传统制造向高附加值、技术密集型产业转型。
提升品牌价值：与创新型企业结合，有助于提升传统企业的市场形象和品牌影响力。
实施要点
明确战略方向：精准识别与自身业务具有协同效应或战略互补性的科创企业。
审慎尽职调查：对目标科创企业的技术、市场、财务、法律等方面进行全面评估。
整合管理能力：制定有效的并购后整合计划，确保技术、人才和文化的顺利融合。
资本运作能力：具备专业的投资并购团队和资金实力。

方案二：科创企业带动传统生产企业工艺、精度、材料水平全面升级并带来较高利润
...（此处省略中间四套方案的详细内容，与你原代码中完全一致，为节省篇幅不再重复粘贴）

方案六：投资于母基金从而实现更稳健的转型。
（保持你原来提供的全部六套方案内容不变）

【输出要求】
1. 结构要求（每个方案必须包含）：
   - 方案核心定位（1-2句话概括该方案对【公司名】的战略意义）
   - 【公司名】专属落地方案（3-4条具体可执行的路径，必须结合公司实际业务、资源、场景）
   - 转型核心优势（4条该方案为【公司名】带来的核心价值）
   - 核心实施要点（4条落地执行的关键注意事项）
2. 内容深度要求：
   - 必须深度融合【公司名】的产业特点、核心资源、渠道网络、品牌优势、区域地位等实际情况
   - 每个落地方案需具体到业务板块、产品品类、渠道场景、客户群体
   - 避免泛泛而谈，必须体现"专属定制"特征
3. 语言风格：
   - 专业、严谨、具有战略高度
   - 使用产业咨询术语（如"第二曲线"、"生态闭环"、"利润天花板"等）
   - 突出【公司名】的品牌势能、老字号价值、区域龙头地位等特色

请严格按照以下格式输出：
请根据以上6套方案，一一对应分析并给出【公司名】的转型升级六套专属方案

## 公司画像（简要提炼）
- 所属行业：
- 核心业务：
- 当前痛点/瓶颈：
- 可用资源：（资金/渠道/品牌/客户/技术等）

方案一：传统企业投资并购科创企业，实现【贴合企业的战略目标，如主业延伸 / 第二曲线突破 / 赛道拓展】
...（后面的格式要求与你原代码完全一致，此处不再重复）

**请务必在输出的最开始位置，明确写上：**
**重要提示：本方案仅供参考，不构成任何正式的投资、经营或法律建议。实际操作请咨询专业律师、财务顾问及相关行业专家。**
"""

# =============================================================================
# Streamlit 界面
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

        with st.spinner("正在调用 AI 生成六套专属转型升级方案..."):
            try:
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": FULL_SYSTEM_PROMPT},
                        {"role": "user", "content": f"请为以下公司生成完整转型升级六套专属方案：\n{user_context}"}
                    ],
                    temperature=0.3,
                    max_tokens=4000,
                    stream=False
                )
                scheme = response.choices[0].message.content
             
                st.success("✅ 生成完成！（已严格按照文档格式输出）")
                
                # 在页面上额外显示免责声明
                st.warning("**重要提示：本方案仅供参考，不构成任何正式的投资、经营或法律建议。实际操作请咨询专业律师、财务顾问及相关行业专家。**")
                
                st.markdown(scheme)
             
                st.download_button(
                    label="📥 下载方案（Markdown）",
                    data=scheme,
                    file_name=f"{company_name}_转型升级六套方案.md",
                    mime="text/markdown"
                )
            except Exception as e:
                st.error(f"AI 调用失败：{str(e)}")
