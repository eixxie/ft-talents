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
st.set_page_config(page_title="相关团队中特定岗位能力分析", page_icon="👔",layout="wide")
st.sidebar.header("Question:\n某个岗位下不同人员的能力差异？ \n 包含同一岗位的不同团队在相关能力项上的平均能力差异？")

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
st.header('相关团队中特定岗位能力分析')
st.caption('📌可以选择一个岗位，查看拥有该岗位的团队在该岗位所需技能的:blue[平均能力]。同时可以选择岗位中若干人员，从而查看他们在岗位所需关键能力上的对比。')
st.divider()
#读取数据
df = pd.read_excel(os.getcwd() + '//' + 'talents.xlsx',index_col=[0])
df_position = pd.read_excel(os.getcwd() + '//' + 'peoples.xlsx',index_col=[0])
df_view = pd.read_excel(os.getcwd() + '//' + 'views.xlsx')
#团队成员指标平均值
df_mean = df.iloc[:,1:].groupby('团队').mean().round(2)

#定义雷达图维度及相应数据
#均值数据
df_tech_mean = df_mean[['产品设计','业务分析','产品运营','安全合规','云网络']]
df_business_mean = df_mean[df_view.query('维度 == "业务知识"').loc[:,'指标'].values.tolist()]
df_diathesis_mean = df_mean[df_view.query('维度 == "通用素质"').loc[:,'指标'].values.tolist()]
#人员数据
df_business = df[df_view.query('维度 == "业务知识"').loc[:,'指标'].values.tolist()]
df_diathesis = df[df_view.query('维度 == "通用素质"').loc[:,'指标'].values.tolist()]
#选择维度
view_col1, view_col2, view_col3, view_col4 = st.columns(4)
with view_col1:
   tech = st.write('请选择要展示的维度')
with view_col2:
   tech = st.checkbox('技术能力', value=True, key='tech_checkbox')
with view_col3:
   business = st.checkbox('业务知识', value=True, key='business_checkbox')
with view_col4:
   diathesis = st.checkbox('通用素质', value=True, key='diathesis_checkbox')


#选择岗位和人员
option = st.selectbox(
    '请选择岗位：',
    df_position.iloc[:, 1].drop_duplicates().dropna().values.tolist())

position_member = df_position.query('岗位 == @option').loc[:,'姓名'].values.tolist()
options = st.multiselect(
    '请选择人员：',
    position_member
)

#获取所选择人员对应的岗位
selected_positons = df_position.query('姓名 in @options').loc[:,'岗位'].drop_duplicates().dropna().values.tolist()
#获取所选择岗位对应的团队
position_teams = df.query('姓名 in @position_member').loc[:,'团队'].drop_duplicates().dropna().values.tolist()
#获取所选择岗位对应的技术指标
select_views = df_view.query('维度 in @option').loc[:,'指标'].drop_duplicates().dropna().values.tolist()
#获取技术指标相应的数据
df_tech = df[select_views]
#获取相应团队的均值数据
df_tech_team_mean = df_mean[select_views]
df_business_team_mean = df_mean[df_view.query('维度 == "业务知识"').loc[:,'指标'].values.tolist()]
df_diathesis_team_mean = df_mean[df_view.query('维度 == "通用素质"').loc[:,'指标'].values.tolist()]

# 定义技术维度的团队均值比较雷达图
radar_tech_team = Radar()
radar_tech_team.add_schema(schema=[
        {"name": col_name, "max": 5, "min": 0} 
        for col_name in df_tech_team_mean.columns
    ])
radar_tech_team.set_global_opts(
    title_opts = opts.TitleOpts(title="技术能力-团队比较"),
)
# 定义业务知识维度的团队均值比较雷达图
radar_business_team = Radar()
radar_business_team.add_schema(schema=[
        {"name": col_name, "max": 5, "min": 0} 
        for col_name in df_business_team_mean.columns
    ])
radar_business_team.set_global_opts(
    title_opts = opts.TitleOpts(title="业务知识-团队比较"),
)
# 定义通用素质维度的团队均值比较雷达图
radar_diathesis_team = Radar()
radar_diathesis_team.add_schema(schema=[
        {"name": col_name, "max": 5, "min": 0} 
        for col_name in df_diathesis_team_mean.columns
    ])
radar_diathesis_team.set_global_opts(
    title_opts = opts.TitleOpts(title="通用素质-团队比较"),
)

#添加团队均值比较雷达图数据
for item in position_teams:
    #st.write('已添加:', item)
    current_color=randomcolor()
    #技术维度
    radar_tech_team.add(
        item,
        [df_tech_team_mean.loc[item].tolist()],
        color = current_color,
        areastyle_opts=opts.AreaStyleOpts(color = current_color,opacity=0.1),
        linestyle_opts=opts.LineStyleOpts(color = current_color,width=1)
    )
    #业务知识维度
    radar_business_team.add(
        item,
        [df_business_team_mean.loc[item].tolist()],
        color = current_color,
        areastyle_opts=opts.AreaStyleOpts(color = current_color,opacity=0.1),
        linestyle_opts=opts.LineStyleOpts(color = current_color,width=1)
    )
    #通用素质维度
    radar_diathesis_team.add(
        item,
        [df_diathesis_team_mean.loc[item].tolist()],
        color = current_color,
        areastyle_opts=opts.AreaStyleOpts(color = current_color,opacity=0.1),
        linestyle_opts=opts.LineStyleOpts(color = current_color,width=1)
    )

# 定义技术维度雷达图-人员比较
radar_tech = Radar()
radar_tech.add_schema(schema=[
        {"name": col_name, "max": 5, "min": 0} 
        for col_name in df_tech.columns
    ])
radar_tech.set_global_opts(
    title_opts = opts.TitleOpts(title="技术能力-人员比较"),
)

# 定义业务知识维度雷达图-人员比较
radar_business = Radar()
radar_business.add_schema(schema=[
        {"name": col_name, "max": 5, "min": 0} 
        for col_name in df_business.columns
    ])
radar_business.set_global_opts(
    title_opts = opts.TitleOpts(title="业务知识-人员比较"),
)

# 定义通用素质维度雷达图-人员比较
radar_diathesis = Radar()
radar_diathesis.add_schema(schema=[
        {"name": col_name, "max": 5, "min": 0}
        for col_name in df_diathesis.columns
    ])
radar_diathesis.set_global_opts(
    title_opts = opts.TitleOpts(title="通用素质-人员比较"),
)

#添加雷达图数据-人员比较
for item in options:
    #st.write('已添加:', item)
    current_color=randomcolor()
    #技术维度
    radar_tech.add(
        item,
        [df_tech.loc[item].tolist()],
        color = current_color,
        areastyle_opts=opts.AreaStyleOpts(color = current_color,opacity=0.1),
        linestyle_opts=opts.LineStyleOpts(color = current_color,width=1)
    )
    #业务知识维度
    radar_business.add(
        item,
        [df_business.loc[item].tolist()],
        color = current_color,
        areastyle_opts=opts.AreaStyleOpts(color = current_color,opacity=0.1),
        linestyle_opts=opts.LineStyleOpts(color = current_color,width=1)
    )
    #通用素质维度
    radar_diathesis.add(
        item,
        [df_diathesis.loc[item].tolist()],
        color = current_color,
        areastyle_opts=opts.AreaStyleOpts(color = current_color,opacity=0.1),
        linestyle_opts=opts.LineStyleOpts(color = current_color,width=1)
    )

#显示技术维度雷达图
if tech and len(select_views) >0:
    tech_col1, tech_col2 = st.columns(2)
    with tech_col1:
        st_pyecharts(radar_tech_team, height="500px", key="tech_team_1")
    with tech_col2:
        st_pyecharts(radar_tech, height="500px", key="tech_personal_1")
#显示业务知识维度雷达图
if business:
    business_col1, business_col2 = st.columns(2)
    with business_col1:
        st_pyecharts(radar_business_team, height="500px", key="business_team_1")
    with business_col2:
        st_pyecharts(radar_business, height="500px", key="business_personal_2")
#显示通用素质维度雷达图
if diathesis:
    diathesis_col1, diathesis_col2 = st.columns(2)
    with diathesis_col1:
        st_pyecharts(radar_diathesis_team, height="500px", key="diathesis_team_1")
    with diathesis_col2:
        st_pyecharts(radar_diathesis, height="500px", key="diathesis_personal_3")