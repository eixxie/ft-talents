# -*- coding: utf-8 -*-
from pickle import NONE
import time,os,random
import streamlit as st
import numpy as np
import pandas as pd
from operator import index
from tokenize import Ignore
from streamlit_echarts import st_pyecharts
from pyecharts.charts import Radar,Line
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
st.set_page_config(page_title="团队人员在特定能力项上的分布分析", page_icon="👀",layout="wide")
st.sidebar.header("Question:\n 不同团队的评分分布/松紧度情况？")

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
st.header('团队人员在特定能力项上的分布分析')
st.caption('📌可以选择一个或若干个团队，从而查看团队成员在选定能力项上的（百分比）分布情况。')
st.divider()
#读取数据
df = pd.read_excel(os.getcwd() + '//' + 'talents.xlsx',index_col=[0])
df_view = pd.read_excel(os.getcwd() + '//' + 'views.xlsx')

#定义雷达图维度及相应数据
df_business = df[df_view.query('维度 == "业务知识"').loc[:,'指标'].values.tolist()]
df_diathesis = df[df_view.query('维度 == "通用素质"').loc[:,'指标'].values.tolist()]

#选择基础素质指标
options_diathesis = st.selectbox(
    '请选择指标：',
    df_view.query('维度 == "通用素质"').loc[:,'指标'].values.tolist())

#选择团队
options_team = st.multiselect(
    '请选择团队：',
    df.iloc[:, 1].drop_duplicates().dropna().values.tolist(),
    ['投研研发3团','营销服务团']
)

#如果选择了基础素质指标，则展示信息，否则不展示
if len(options_diathesis)!=0:
    #如果未选择团队，则统计整体情况，否则统计相应团队的情况
    if len(options_team) == 0:
        pivot_team = df.pivot_table(columns = "".join(options_diathesis),values = '姓名',aggfunc='count',fill_value=0) 
    else:
        pivot_team = df.pivot_table(index = '团队',columns = "".join(options_diathesis),values = '姓名',aggfunc='count',fill_value=0) \
                        .query('团队 in @options_team')
    #统计各个评分项的百分比信息，如果统计信息缺列，则自动补0
    for item in list(set([1,2,3,4,5]).difference(set(pivot_team.columns.tolist()))):
        pivot_team[item] = 0
    #st.write(pivot_team.loc[:,[1,2,3,4,5]])
    #将数量统计转化为百分比
    pivot_team = pivot_team.loc[:,[1,2,3,4,5]].div(pivot_team.sum(axis=1), axis=0).round(2)

    #st.write(pivot_team)
    #st.write(pivot_team.columns.to_list())

    #定义面积堆叠图
    area_Chart = Line()
    area_Chart.set_global_opts(title_opts=opts.TitleOpts(title="团队成员在该指标上的评分分布"))
    area_Chart.add_xaxis(['1','2','3','4','5'])
    for item in pivot_team.index:
        current_color=randomcolor()
        area_Chart.add_yaxis(
            item,
            pivot_team.loc[item].tolist(),
            color = current_color,
            areastyle_opts=opts.AreaStyleOpts(color = current_color,opacity=0.3),
            linestyle_opts=opts.LineStyleOpts(color = current_color,width=1),
            label_opts=opts.LabelOpts(is_show=False),
            is_smooth = True,# 平滑曲线
            #stack="pileup",# 设置堆积图
        )

    #展示面积堆叠图
    st_pyecharts(area_Chart, height="600px", key="2")

