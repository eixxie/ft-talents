# -*- coding: utf-8 -*-
from sys import maxsize
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
st.set_page_config(page_title="能力项符合性检索", page_icon="❤",layout="wide")
st.sidebar.header("Question:\n 谁最能满足特定能力项的标准？")

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
st.header('能力项符合性检索')
st.caption('📌可以选择一个或若干个能力项指标，从而查看在这些能力项上的得分均大于等于所定阈值的人员，及其在相应能力项上的得分情况。')
st.divider()
#读取数据
df = pd.read_excel(os.getcwd() + '//' + 'talents.xlsx',index_col=[0])
df_position = pd.read_excel(os.getcwd() + '//' + 'peoples.xlsx',index_col=[0])
df_view = pd.read_excel(os.getcwd() + '//' + 'views.xlsx')

#定义雷达图维度及相应数据
df_business = df[df_view.query('维度 == "业务知识"').loc[:,'指标'].values.tolist()]
df_diathesis = df[df_view.query('维度 == "通用素质"').loc[:,'指标'].values.tolist()]

#选择各维度关注的指标
#title = st.write('请选择查询指标')
view_col1, view_col2 ,view_col3 = st.columns([2,1,1])
with view_col1:
   #选择阈值
    options_value = st.multiselect(
        '得分阈值：',
        ['5','4','3','2','1'],['5'],max_selections=1,
        key = 'value_mselect'
    )
with view_col2:
   st.write('阈值比较模式：')
   tech_checkbox = st.checkbox('小于等于', value=False,help='如不选择此项，则默认筛选大于等于阈值的情况', key='tech_checkbox')
with view_col3:
   st.write('筛选方式：')
   or_mode_checkbox = st.checkbox('OR模式', value=False,help='选择多个指标时，默认为And模式，勾选此项改为OR模式', key='or_mode_checkbox')

#选择技术能力指标
options_tech = st.multiselect(
    '技术能力指标：',
    df_view.query('维度 == "技术能力"').loc[:,'指标'].values.tolist(),
    key = 'tech_mselect'
)
#选择业务知识指标
options_business = st.multiselect(
    '业务知识指标：',
    df_view.query('维度 == "业务知识"').loc[:,'指标'].values.tolist(),
    key = 'business_mselect'
)
#选择基础素质指标
options_diathesis = st.multiselect(
    '基础素质指标：',
    df_view.query('维度 == "通用素质"').loc[:,'指标'].values.tolist(),
    key = 'diathesis_mselect'
)

#将查询条件进行组合
options = options_tech + options_business + options_diathesis
#st.write(options)

#查询所选择的维度均大于3的人员
query_string = ""
compare_type = ''
link_type = ''
compare_type='<=' if tech_checkbox  else '>='
link_type = ' | ' if or_mode_checkbox else ' & '
for item in options:
    query_string += item + compare_type + "".join(options_value) + link_type
#st.write(query_string[:-2])


#按照查询结果中每行记录的平均值从大到小排序
if query_string!="" and len(options_value)>0:
    df_compare = df.query(query_string[:-2]).loc[:,options]
    df_compare['mean'] = df_compare.mean(axis=1)
    df_compare = df_compare.sort_values('mean', ascending=False).drop('mean', axis=1)
    st.write('查询结果明细：')
    st.write(df_compare)

    # 定义人员对比雷达图
    radar_compare = Radar()
    radar_compare.add_schema(schema=[
            {"name": col_name, "max": 5, "min": 0} 
            for col_name in df_compare.columns
        ])
    radar_compare.set_global_opts(
        title_opts = opts.TitleOpts(title="人员对比"),
    )

    #添加雷达图数据
    for item in df_compare.index:
        #st.write('已添加:', item)
        current_color=randomcolor()
        #业务知识维度
        radar_compare.add(
            item,
            [df_compare.loc[item].tolist()],
            color = current_color,
            areastyle_opts=opts.AreaStyleOpts(color = current_color,opacity=0.1),
            linestyle_opts=opts.LineStyleOpts(color = current_color,width=1)
        )

    #展示雷达图
    st_pyecharts(radar_compare, height="500px", key="2")