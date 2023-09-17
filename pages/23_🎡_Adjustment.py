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
st.set_page_config(page_title="非在岗人员的岗位胜任力分析", page_icon="🎡",layout="wide")
st.sidebar.header("Question:\n 谁可以无缝调岗？")

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
st.header('非在岗人员的岗位胜任力分析')
st.caption('📌可以选择一个岗位，从而查看不在这个岗位上但与该岗位技术能力要求最接近的前5个人员。')
st.divider()
#读取数据
df = pd.read_excel(os.getcwd() + '//' + 'talents.xlsx',index_col=[0])
df_position = pd.read_excel(os.getcwd() + '//' + 'peoples.xlsx',index_col=[0])
df_view = pd.read_excel(os.getcwd() + '//' + 'views.xlsx')
#获取所有岗位
all_positons = df_position.loc[:,'岗位'].drop_duplicates().dropna().values.tolist()
#生成每个人在每个岗位上的技术能力分
for item in all_positons:
    df[item] = df[df_view.query('维度 == @item').loc[:,'指标'].values.tolist()].mean(axis=1).round(2)
df_match = df[all_positons]

#筛选选项
view_col1, view_col2 = st.columns([1,3])
with view_col1:
    #选择岗位和人员
    option = st.selectbox(
        '请选择岗位：',
        df_position.iloc[:, 1].drop_duplicates().dropna().values.tolist())
    #岗位对应人员
    position_member = df_position.query('岗位 == @option').loc[:,'姓名'].values.tolist()
    #与岗位能力要求最接近的人员
    df_similarity = df.sort_values(option,ascending=False).drop(position_member).loc[:,option].head(5)
with view_col2:
    #选择人员以查看具体能力情况
    options = st.multiselect(
        '请选择人员，查看详细情况：',
        df_similarity.index.values.tolist() + position_member
    )

#
st.write('以下是与该岗位技术能力要求最接近的非在岗人员：')
st.write(df_similarity)

#获取所选择人员对应的岗位
selected_positons = df_position.query('姓名 in @options').loc[:,'岗位'].drop_duplicates().dropna().values.tolist()
#获取所选择岗位对应的团队
position_teams = df.query('姓名 in @position_member').loc[:,'团队'].drop_duplicates().dropna().values.tolist()
#获取所选择岗位对应的技术指标
select_views = df_view.query('维度 in @option').loc[:,'指标'].drop_duplicates().dropna().values.tolist()
#获取技术指标相应的数据
df_tech = df[select_views]

# 定义雷达图
# 定义岗位匹配雷达图
radar_match = Radar()
radar_match.add_schema(schema=[
        {"name": item, "max": 5, "min": 0} 
        for item in all_positons
    ])
radar_match.set_global_opts(
    title_opts = opts.TitleOpts(title="岗位匹配"),
)
# 定义技术维度雷达图
radar_tech = Radar()
radar_tech.add_schema(schema=[
        {"name": col_name, "max": 5, "min": 0} 
        for col_name in df_tech.columns
    ])
radar_tech.set_global_opts(
    title_opts = opts.TitleOpts(title="核心技术能力"),
)

#添加雷达图数据
for item in options:
    #st.write('已添加:', item)
    current_color=randomcolor()
    #岗位匹配
    radar_match.add(
        item,
        [df_match.loc[item].tolist()],
        color = current_color,
        areastyle_opts=opts.AreaStyleOpts(color = current_color,opacity=0.1),
        linestyle_opts=opts.LineStyleOpts(color = current_color,width=1)
    )
    #技术维度
    radar_tech.add(
        item,
        [df_tech.loc[item].tolist()],
        color = current_color,
        areastyle_opts=opts.AreaStyleOpts(color = current_color,opacity=0.1),
        linestyle_opts=opts.LineStyleOpts(color = current_color,width=1)
    )

#如果选了人，就显示岗位匹配和技术维度雷达图
if len(options)>0 and len(select_views) >0:
    tech_col1, tech_col2 = st.columns([2,2])
    with tech_col1:
        st_pyecharts(radar_match, height="500px", key="tech_team_1")
    with tech_col2:
        st_pyecharts(radar_tech, height="500px", key="tech_personal_1")