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
st.set_page_config(page_title="能力偏向分析", page_icon="👍",layout="wide")
st.sidebar.header("Question:\n 不同能力项下的头部及尾部人员是谁？")

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
st.header('能力偏向分析')
st.caption('📌可以选择一个或若干个指标，从而查看该指标下（均值）排名前10及后10的人员。')
st.divider()
#读取数据
df = pd.read_excel(os.getcwd() + '//' + 'talents.xlsx',index_col=[0])
df_position = pd.read_excel(os.getcwd() + '//' + 'peoples.xlsx',index_col=[0])
df_view = pd.read_excel(os.getcwd() + '//' + 'views.xlsx')

#定义雷达图维度及相应数据
df_business = df[df_view.query('维度 == "业务知识"').loc[:,'指标'].values.tolist()]
df_diathesis = df[df_view.query('维度 == "通用素质"').loc[:,'指标'].values.tolist()]

#选择各维度关注的指标
view_col1, view_col2 ,view_col3,view_col4 = st.columns([2,4,4,4])
with view_col1:
    st.write('请选择要分析的指标集：')
with view_col2:
    #选择技术能力指标
    options_tech = st.multiselect(
        '技术能力指标：',
        df_view.query('维度 == "技术能力"').loc[:,'指标'].values.tolist(),
        key = 'tech_mselect'
    )
with view_col3:
    #选择业务知识指标
    options_business = st.multiselect(
        '业务知识指标：',
        df_view.query('维度 == "业务知识"').loc[:,'指标'].values.tolist(),
        key = 'business_mselect'
    )
with view_col4:
    #选择基础素质指标
    options_diathesis = st.multiselect(
        '基础素质指标：',
        df_view.query('维度 == "通用素质"').loc[:,'指标'].values.tolist(),
        key = 'diathesis_mselect'
    )

#将查询条件进行组合
options = options_tech + options_business + options_diathesis
st.divider()

#按照查询结果中每行记录的平均值从大到小排序
if len(options)>0:
    df_result = df.loc[:,options]
    df_result['均值'] = df_result.mean(axis=1).round(2)
    result_col1, result_col2  = st.columns([1,1])
    with result_col1:
        st.write('前10人：')
        st.write(df_result.sort_values('均值',ascending=False).head(10))
    with result_col2:
        st.write('后10人：')
        st.write(df_result.sort_values('均值',ascending=False).tail(10))