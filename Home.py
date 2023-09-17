import streamlit as st
import streamlit_authenticator as stauth
from streamlit_authenticator import Authenticate
import yaml,os
from yaml.loader import SafeLoader
with open(os.getcwd() + '//' + 'config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

st.set_page_config(
    page_title="FT-Talents",
    page_icon="👋", 
)

# #生成密码对应的hash值
# hashed_passwords = stauth.Hasher(['admin888', 'mingming']).generate()
# st.write(hashed_passwords)

#用户登录
authenticator = Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)
#用户登录窗口
name, authentication_status, username = authenticator.login('登录', 'main')
#用户登录后操作
if authentication_status:
    authenticator.logout('退出', 'sidebar')
elif authentication_status == False:
    st.error('用户名 或 密码不正确')
    st.stop()
elif authentication_status == None:
    st.warning('请输入您的用户名和密码')
    st.stop()

st.write("# ⛳金科人才评估报告")
st.sidebar.success("Select a demo above.")
st.markdown(
    """
    为支持各级管理者充分了解员工能力、素质和个性，为后续招聘、培训、培养、岗位安排提供必要的信息，2023年8~9月组织对员工能力进行了全面评估。
    ### 评估范围包括什么？
    - 技术能力：对工作所需主要技能的掌握和应用程度，含不同岗位所需的62个评估项（并集）
    - 业务能力：对公司各业务领域知识的掌握和应用程度，含20个评估项
    - 基础素质：综合利用技术和业务能力达成工作目标的潜质，含10个评估项

    ### 有什么用？
    - 查看员工的能力
    - 对比不同员工的能力
    - 分析不同团队的能力及人员梯队
    - 识别具有相似能力组合的人员
    - 识别具备岗位胜任力的非在岗人员
    - 查阅人员在人才地图上的分布
    - 查阅整体、岗位、团队在各类能力项上的优势和不足
    - 检索特定能力较强/较弱的人员

    ### 信息准确吗？
    评价方式为主观评价（1-5档），但经过了校准过程：
    - 技术能力：团队长评价、技术委员会校准
    - 业务能力：团队长评价、团队长的各层上级逐级（直至部门总）校准
    - 基础素质：团队长评价、团队长的各层上级逐级（直至部门总）校准

"""
)