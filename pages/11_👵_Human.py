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
st.set_page_config(page_title="人员能力分析", page_icon="👵",layout="wide")
st.sidebar.header("Question:\n某个人的能力怎么样？ \n 某几个人的能力差异在什么地方？")

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
st.header('人员能力分析')
st.caption('📌可以选择一个或若干个人员，从而查看他们在各个能力上的对比。岗位匹配指相应人员在相应岗位所需关键技术能力上的得分情况。')
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


#定义雷达图维度及相应数据
df_match = df[all_positons]
#df_tech = df[['产品设计','业务分析','产品运营','PMP','Python','安全合规','云网络']]
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

#选择人员
options = st.multiselect(
    '请选择人员：',
    df.loc[:,'姓名'].values.tolist(),['李卓颂','唐昊喜']
)
#获取所选择人员对应的岗位
selected_positons = df_position.query('姓名 in @options').loc[:,'岗位'].drop_duplicates().dropna().values.tolist()
#获取所选择岗位对应的指标
select_views = df_view.query('维度 in @selected_positons').loc[:,'指标'].drop_duplicates().dropna().values.tolist()
#获取对应指标相应的数据
df_tech = df[select_views]
#st.write(df_tech)

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
    title_opts = opts.TitleOpts(title="技术能力"),
)
# 定义业务知识维度雷达图
radar_business = Radar()
radar_business.add_schema(schema=[
        {"name": col_name, "max": 5, "min": 0} 
        for col_name in df_business.columns
    ])
radar_business.set_global_opts(
    title_opts = opts.TitleOpts(title="业务知识"),
)
# 定义通用素质维度雷达图
radar_diathesis = Radar()
radar_diathesis.add_schema(schema=[
        {"name": col_name, "max": 5, "min": 0} 
        for col_name in df_diathesis.columns
    ])
radar_diathesis.set_global_opts(
    title_opts = opts.TitleOpts(title="通用素质"),
)

#添加雷达图数据
for item in options:
    #st.write('已添加:', item )
    #st.write(df_tech.loc[item])
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


#显示岗位匹配、技术维度雷达图
if tech:
    tech_col1, tech_col2 = st.columns(2)
    with tech_col1:
        st_pyecharts(radar_match, height="500px", key="1")
    with tech_col2:
        st_pyecharts(radar_tech, height="500px", key="2")
#显示业务知识、通用素质维度雷达图
business_col, diathesis_col = st.columns(2)
with business_col:
    if business:
        st_pyecharts(radar_business, height="500px", key="3")
with diathesis_col:    
    if diathesis:
        st_pyecharts(radar_diathesis, height="500px", key="4")