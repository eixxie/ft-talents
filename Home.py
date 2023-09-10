import streamlit as st

st.set_page_config(
    page_title="FT-Talents",
    page_icon="👋", 
)

st.write("# 金科人才评估报告 👋")

st.sidebar.success("Select a demo above.")

st.markdown(
    """
    为支持各级管理者充分了解员工能力、素质和个性，为后续招聘、培训、培养、岗位安排提供必要的信息，组织对员工能力进行了全面评估。
    ### 评估范围覆盖了三个维度：
    - 技术能力：对工作所需主要技能的掌握和应用程度
    - 业务能力：对公司各业务领域知识的掌握和应用程度
    - 基础素质：综合利用技术和业务能力达成工作目标的潜质

    评估时间：2023年8~9月
"""
)