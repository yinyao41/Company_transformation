import streamlit as st
import os

st.set_page_config(page_title="转型升级方案", layout="wide", page_icon="🏭")

st.title("🏭 企业转型升级八套方案生成器")
st.caption("📌 简化版 · 无需 OpenAI · 快速生成")

# 输入区域
with st.form("transform_form"):
    col1, col2 = st.columns(2)
    with col1:
        company_name = st.text_input("公司名称 *", placeholder="山东固丰体育产业有限公司")
        industry = st.text_input("所属行业 *", placeholder="体育用品制造")
    with col2:
        scale = st.text_input("公司规模", placeholder="年营收约2亿元，员工300人")

    current_status = st.text_area(
        "公司当前情况 *", 
        height=180,
        placeholder="请详细描述：主营业务、核心优势、面临痛点（如利润下滑、渠道老化、竞争激烈）、可用资源（品牌、经销商网络、资金等）..."
    )
    
    submit = st.form_submit_button("🚀 生成八套转型升级方案", type="primary")

if submit:
    if not company_name or not industry or not current_status:
        st.error("请填写带 * 的必填项")
    else:
        st.success(f"✅ 已为 **{company_name}** 生成方案")
        st.warning("**重要提示：本方案为模板演示，仅供参考，不构成任何投资或经营建议。请结合专业顾问意见使用。**")

        # ==================== 模拟生成内容 ====================
        st.markdown("## 公司画像（简要提炼）")
        st.markdown(f"""
- **所属行业**：{industry}
- **核心业务**：{current_status[:150]}...
- **当前痛点**：利润率下滑、传统业务天花板、数字化程度较低
- **可用资源**：品牌优势、渠道网络、区域地位
        """)

        schemes = [
            "投资并购科创企业",
            "科创带动工艺升级",
            "数智化转型升级",
            "经销商升级高毛利科创产品",
            "精益管理转型升级",
            "经销商持股科创企业",
            "成为科创基金股东",
            "投资母基金（FoF）"
        ]

        for i, title in enumerate(schemes, 1):
            with st.expander(f"方案{i}：{title}", expanded=(i==1)):
                st.markdown(f"**方案核心定位**")
                st.write(f"通过{title}帮助{company_name}突破传统业务利润天花板，构建第二增长曲线。")
                
                st.markdown("**专属落地方案**")
                st.write("1. 结合主业寻找协同科创标的")
                st.write("2. 利用现有渠道和品牌资源加速整合")
                st.write("3. 设立专项基金或联合地方政府支持")
                
                st.markdown("**转型核心优势**")
                st.write("- 快速获取新技术与新赛道")
                st.write("- 提升品牌科技形象")
                st.write("- 实现多元化经营")
                st.write("- 增强长期竞争力")
                
                st.markdown("**核心实施要点**")
                st.write("1. 做好尽职调查与风险评估")
                st.write("2. 制定清晰的整合计划")
                st.write("3. 组建专业团队负责")
                st.write("4. 分阶段推进，控制节奏")
        
        # 下载按钮
        markdown_content = f"# {company_name} 转型升级八套方案\n\n（此处为简化模板演示）"
        st.download_button(
            label="📥 下载方案（Markdown）",
            data=markdown_content,
            file_name=f"{company_name}_转型升级方案.md",
            mime="text/markdown"
        )

st.info("💡 当前为简化演示版。描述越详细，生成的定制化内容越精准。")
