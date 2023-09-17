# -*- coding: utf-8 -*-
import time,os,random
import streamlit as st
import numpy as np
import pandas as pd
from operator import index
from tokenize import Ignore
from streamlit_echarts import st_pyecharts
from pyecharts.charts import Radar
from pyecharts import options as opts
import streamlit_authenticator as stauth
from streamlit_authenticator import Authenticate
import yaml,os
from yaml.loader import SafeLoader
with open(os.getcwd() + '//' + 'config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

#随机生成颜色
def randomcolor():
    colorArr = ['1','2','3','4','5','6','7','8','9','A','B','C','D','E','F']
    color = ""
    for i in range(6):
        color += colorArr[random.randint(0,14)]
    return "#"+color

#设置页面全局参数
st.set_page_config(page_title="团队能力分析", page_icon="💢",layout="wide")
st.sidebar.header("Question:\n 不同团队的成员平均能力的最大值及标准差？")

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
    
#设置页面标题
st.header('团队能力分析')
st.caption('📌可以选择一个或若干个团队，从而查看他们在各个所需能力（团队人员所在岗位所需能力项的∪并集）上的最大值和标准差（只包括必须具备相关能力的人员）。')
st.divider()
#读取数据
df = pd.read_excel(os.getcwd() + '//' + 'talents.xlsx',index_col=[0])
#团队成员指标最大值
df_mean = df.iloc[:,1:].groupby('团队').max().round(2)
#团队成员指标标准差
df_std = df.iloc[:,1:].groupby('团队').std().round(2)
df_position = pd.read_excel(os.getcwd() + '//' + 'peoples.xlsx',index_col=[0])
df_view = pd.read_excel(os.getcwd() + '//' + 'views.xlsx')

#定义雷达图维度及相应数据
df_business_mean = df_mean[df_view.query('维度 == "业务知识"').loc[:,'指标'].values.tolist()]
df_diathesis_mean = df_mean[df_view.query('维度 == "通用素质"').loc[:,'指标'].values.tolist()]
df_business_std = df_std[df_view.query('维度 == "业务知识"').loc[:,'指标'].values.tolist()]
df_diathesis_std = df_std[df_view.query('维度 == "通用素质"').loc[:,'指标'].values.tolist()]

#选择维度
col1, col2, col3, col4 = st.columns(4)
with col1:
   tech = st.write('请选择要展示的维度：')
with col2:
   tech = st.checkbox('技术能力', value=True, key='tech_checkbox')
with col3:
   business = st.checkbox('业务知识', value=True, key='business_checkbox')
with col4:
   diathesis = st.checkbox('通用素质', value=True, key='diathesis_checkbox')


#选择人员
options = st.multiselect(
    '请选择团队：',
    df_mean.index.values.tolist()
    ,['投研研发3团','营销服务团']
    )
team_member = df.query('团队 in @options').loc[:,'姓名'].values.tolist()

#获取所选择人员对应的岗位
selected_positons = df_position.query('姓名 in @team_member').loc[:,'岗位'].drop_duplicates().dropna().values.tolist()
#获取所选择岗位对应的指标
select_views = df_view.query('维度 in @selected_positons').loc[:,'指标'].drop_duplicates().dropna().values.tolist()
#获取对应指标相应的数据
df_tech_mean = df_mean[select_views]
df_tech_std = df_std[select_views]

# 定义技术维度雷达图-均值
radar_tech_mean = Radar()
radar_tech_mean.add_schema(schema=[
        {"name": col_name, "max": 5, "min": 0} 
        for col_name in df_tech_mean.columns
    ])
radar_tech_mean.set_global_opts(
    title_opts = opts.TitleOpts(title="技术能力-最大值"),
)

# 定义业务知识维度雷达图-均值
radar_business_mean = Radar()
radar_business_mean.add_schema(schema=[
        {"name": col_name, "max": 5, "min": 0} 
        for col_name in df_business_mean.columns
    ])
radar_business_mean.set_global_opts(
    title_opts = opts.TitleOpts(title="业务知识-最大值"),
)

# 定义通用素质维度雷达图-均值
radar_diathesis_mean = Radar()
radar_diathesis_mean.add_schema(schema=[
        {"name": col_name, "max": 5, "min": 0} 
        for col_name in df_diathesis_mean.columns
    ])
radar_diathesis_mean.set_global_opts(
    title_opts = opts.TitleOpts(title="通用素质-最大值"),
)
# 定义技术维度雷达图-标准差
radar_tech_std = Radar()
radar_tech_std.add_schema(schema=[
        {"name": col_name, "max": 2, "min": 0} 
        for col_name in df_tech_std.columns
    ])
radar_tech_std.set_global_opts(
    title_opts = opts.TitleOpts(title="技术能力-标准差"),
)

# 定义业务知识维度雷达图-标准差
radar_business_std = Radar()
radar_business_std.add_schema(schema=[
        {"name": col_name, "max": 3, "min": 0} 
        for col_name in df_business_std.columns
    ])
radar_business_std.set_global_opts(
    title_opts = opts.TitleOpts(title="业务知识-标准差"),
)

# 定义通用素质维度雷达图-标准差
radar_diathesis_std = Radar()
radar_diathesis_std.add_schema(schema=[
        {"name": col_name, "max": 3, "min": 0} 
        for col_name in df_diathesis_std.columns
    ])
radar_diathesis_std.set_global_opts(
    title_opts = opts.TitleOpts(title="通用素质-标准差"),
)

#添加雷达图数据
for item in options:
    current_color=randomcolor()
    #技术维度-均值
    radar_tech_mean.add(
        item,
        [df_tech_mean.loc[item].tolist()],
        color = current_color,
        areastyle_opts=opts.AreaStyleOpts(color = current_color,opacity=0.1),
        linestyle_opts=opts.LineStyleOpts(color = current_color,width=1)
    )
    #业务知识维度-均值
    radar_business_mean.add(
        item,
        [df_business_mean.loc[item].tolist()],
        color = current_color,
        areastyle_opts=opts.AreaStyleOpts(color = current_color,opacity=0.1),
        linestyle_opts=opts.LineStyleOpts(color = current_color,width=1)
    )
    #通用素质维度-均值
    radar_diathesis_mean.add(
        item,
        [df_diathesis_mean.loc[item].tolist()],
        color = current_color,
        areastyle_opts=opts.AreaStyleOpts(color = current_color,opacity=0.1),
        linestyle_opts=opts.LineStyleOpts(color = current_color,width=1)
    )
    #技术维度-标准差
    radar_tech_std.add(
        item,
        [df_tech_std.loc[item].tolist()],
        color = current_color,
        areastyle_opts=opts.AreaStyleOpts(color = current_color,opacity=0.1),
        linestyle_opts=opts.LineStyleOpts(color = current_color,width=1)
    )
    #业务知识维度-标准差
    radar_business_std.add(
        item,
        [df_business_std.loc[item].tolist()],
        color = current_color,
        areastyle_opts=opts.AreaStyleOpts(color = current_color,opacity=0.1),
        linestyle_opts=opts.LineStyleOpts(color = current_color,width=1)
    )
    #通用素质维度-标准差
    radar_diathesis_std.add(
        item,
        [df_diathesis_std.loc[item].tolist()],
        color = current_color,
        areastyle_opts=opts.AreaStyleOpts(color = current_color,opacity=0.1),
        linestyle_opts=opts.LineStyleOpts(color = current_color,width=1)
    )


#显示技术维度雷达图
if tech:
    tech_col1, tech_col2 = st.columns(2)
    with tech_col1:
        st_pyecharts(radar_tech_mean, height="500px", key="mean_1")
    with tech_col2:
        st_pyecharts(radar_tech_std, height="500px", key="std_1")
#显示业务知识维度雷达图
if business:
    business_col1, business_col2 = st.columns(2)
    with business_col1:
        st_pyecharts(radar_business_mean, height="500px", key="mean_2")
    with business_col2:    
        st_pyecharts(radar_business_std, height="500px", key="std_2")
#显示通用素质维度雷达图
if diathesis:
    diathesis_col1, diathesis_col2 = st.columns(2)
    with diathesis_col1:    
        st_pyecharts(radar_diathesis_mean, height="500px", key="mean_3")
    with diathesis_col2:     
        st_pyecharts(radar_diathesis_std, height="500px", key="std_3")

