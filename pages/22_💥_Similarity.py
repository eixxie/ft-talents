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
st.set_page_config(page_title="人员相似度分析", page_icon="💥",layout="wide")
st.sidebar.header("Question:\n 谁和某个人的能力最相近？")

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
st.header('人员相似度分析')
st.caption('📌可以选择一个人员，查看与他核心能力项(技术能力表现为熟练及以上)集合最相似的前5个人员。相似度根据能力项评分差异/比较项数量来计算，差异0分时权重为1，差异1分时权重为0.2。相似度0.8以上可以认为是较为相似。')
st.divider()
#读取数据
df = pd.read_excel(os.getcwd() + '//' + 'talents.xlsx',index_col=[0])
df_position = pd.read_excel(os.getcwd() + '//' + 'peoples.xlsx',index_col=[0])
df_view = pd.read_excel(os.getcwd() + '//' + 'views.xlsx')

#选择维度
col1, col2, col3, col4 = st.columns(4)
with col1:
   tech = st.write('请选择要比较的维度：')
with col2:
   tech_checkbox = st.checkbox('技术能力', value=False, key='tech_checkbox')
with col3:
   business_checkbox = st.checkbox('业务知识', value=False, key='business_checkbox')
with col4:
   diathesis_checkbox = st.checkbox('通用素质', value=True, key='diathesis_checkbox')


#选择人员
options = st.multiselect(
    '请选择人员：',
    df.loc[:,'姓名'].values.tolist(),['李卓颂'],max_selections=1,
)

#获取所选择人员对应的岗位
selected_positons = df_position.query('姓名 in @options').loc[:,'岗位'].drop_duplicates().dropna().values.tolist()
#获取所选择岗位对应的技术指标
#views_tech = df_view.query('维度 in @selected_positons').loc[:,'指标'].drop_duplicates().dropna().values.tolist()
#获取所选择人员大于2分的技能对应的技术指标
df_T = df.query('姓名 in @options').iloc[:,39:].T
#st.write(df_T[df_T > 2].dropna())
views_tech = df_T[df_T > 2].dropna().index.tolist()
#获取业务知识和通用素质指标
views_business = df_view.query('维度 == "业务知识"').loc[:,'指标'].values.tolist()
views_diathesis = df_view.query('维度 == "通用素质"').loc[:,'指标'].values.tolist()
#获取对应指标相应的数据
views_similarity = []
if tech_checkbox: views_similarity += views_tech
if business_checkbox: views_similarity += views_business
if diathesis_checkbox: views_similarity += views_diathesis
df_similarity = df[views_similarity]

# 相对于所选人员计算差异
if len(options)!=0:
    # 明确所选人员
    specified_row = df.loc["".join(options)]
    # 使用apply函数和lambda表达式来计算其他人相对于所选人员的差异
    df_similarity_difference = df_similarity.apply(lambda row: row - specified_row, axis=1).loc[:,views_similarity]
    #计算相似度
    df_similarity['相似度'] = df_similarity_difference.apply(lambda row: ((row == 0).sum()+(row == 1).sum()/5+(row == -1).sum()/5) / len(row), axis=1)#.apply(lambda x:format(x,'.0%'))
    #st.write(df_similarity.sort_values('相似度',ascending=False))
    #按照相似度降序排列取相似度最高的前5人，并去掉相似度列
    df_similarity_rate = df_similarity.sort_values('相似度',ascending=False).loc[:,'相似度'].head(5)
    df_similarity = df_similarity.sort_values('相似度',ascending=False).drop('相似度', axis=1).head(5)
    #st.write(df_similarity)

    # 定义人员相似度比较雷达图
    radar_similarity = Radar()
    radar_similarity.add_schema(schema=[
            {"name": col_name, "max": 5, "min": 0} 
            for col_name in df_similarity.columns
        ])
    radar_similarity.set_global_opts(
        title_opts = opts.TitleOpts(title="人员相似度比较"),
    )

    #添加人员相似度比较雷达图数据
    for item in df_similarity.index:
        #st.write('已添加:', item)
        current_color=randomcolor()
        #技术维度-标准差
        radar_similarity.add(
            item,
            [df_similarity.loc[item].tolist()],
            color = current_color,
            areastyle_opts=opts.AreaStyleOpts(color = current_color,opacity=0.1),
            linestyle_opts=opts.LineStyleOpts(color = current_color,width=1)
        )

    #显示人员相似度比较雷达图
    if tech_checkbox or business_checkbox or diathesis_checkbox:
        table_col, chart_col = st.columns([1, 3])
        #输出相似度明细
        with table_col: st.write(df_similarity_rate)
        #输出雷达图
        with chart_col: st_pyecharts(radar_similarity, height="500px", key="1")