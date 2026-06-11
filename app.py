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

# 使用更快模型（推荐）
MODEL_NAME = "qwen-plus"   # 比 qwen-max 更快，可改为 "qwen-max" 测试

# =============================================================================
# 极致精简版系统提示词（核心加速点）
# =============================================================================
FULL_SYSTEM_PROMPT = """你是一位顶级产业战略咨询专家。
请为用户公司生成**八套转型升级专属方案**。

八套方案名称：
1. 投资并购科创企业
2. 科创带动工艺升级
3. 数智化转型升级
4. 经销商升级高毛利科创产品
5. 精益管理转型升级
6. 经销商持股科创企业
7. 成为科创基金股东
8. 投资母基金（FoF）

输出要求：
- 最前面加免责声明：**重要提示：本方案仅供参考，不构成投资或法律建议。**
- 先输出 ## 公司画像
- 然后依次输出方案一至八，每套严格包含：
  1. 方案核心定位（1-2句）
  2. [公司名]专属落地方案（3-4条，结合公司实际）
  3. 转型核心优势（4条）
  4. 核心实施要点（4条）
- 语言专业、定制化强，突出公司品牌与资源。
- 控制总长度，内容精炼有力。"""

# =============================================================================
# Streamlit 界面
# =============================================================================
st.set_page_config(page_title="转型升级方案", layout="wide", page_icon="🏭")
st.title("🏭 企业转型升级八套方案生成器")
st.caption("🚀 优化版 · 响应更快 · 支持流式输出")

with st.form("company_form"):
    col1, col2 = st.columns([1, 1])
    with col1:
        company_name = st.text_input("公司名称 *", placeholder="山东固丰体育产业有限公司")
        industry = st.text_input("所属行业 *", placeholder="体育用品 / 纺织 / 机械制造")
    with col2:
        company_size = st.text_input("公司规模", placeholder="年营收约X亿，员工X人")

    current_status = st.text_area("公司当前情况 *", 
                                  placeholder="请详细描述主营业务、核心优势、痛点（如利润下滑、渠道老化）、资源（品牌、经销商网络等）...", 
                                  height=160)
    
    additional_info = st.file_uploader("上传补充文件（可选）", type=["docx", "pdf", "txt"])
    submit = st.form_submit_button("🚀 生成八套方案", type="primary")

if submit:
    if not company_name or not industry or not current_status:
        st.error("请填写带 * 的必填项")
    else:
        # 读取附件
        extra_text = ""
        if additional_info:
            try:
                if additional_info.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    doc = Document(BytesIO(additional_info.read()))
                    extra_text = "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip()])[:800]
                else:
                    extra_text = additional_info.read().decode("utf-8", errors="ignore")[:800]
            except:
                extra_text = "(文件读取失败)"

        user_input = f"""
公司名称：{company_name}
所属行业：{industry}
规模：{company_size}
当前情况：{current_status}
补充信息：{extra_text}
"""

        st.info("🔄 AI 正在思考并生成方案，请耐心等待...（通常 25-50 秒）")
        
        try:
            with st.spinner("生成中..."):
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": FULL_SYSTEM_PROMPT},
                        {"role": "user", "content": f"请为以下公司生成八套转型升级方案：\n{user_input}"}
                    ],
                    temperature=0.3,
                    max_tokens=7000,
                    stream=True   # ← 开启流式输出，极大改善用户体验
                )

                # 流式显示
                result_placeholder = st.empty()
                full_response = ""
                
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                        result_placeholder.markdown(full_response + "▌")
                
                result_placeholder.markdown(full_response)

            st.success("✅ 方案生成完成！")
            
            st.download_button(
                "📥 下载 Markdown 文件",
                data=full_response,
                file_name=f"{company_name}_八套转型升级方案.md",
                mime="text/markdown"
            )
            
        except Exception as e:
            st.error(f"生成失败: {str(e)}")

st.caption("💡 提示：描述越详细，方案针对性越强。首次加载后会明显变快。")
