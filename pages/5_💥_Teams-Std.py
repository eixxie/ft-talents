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


#随机生成颜色
def randomcolor():
    colorArr = ['1','2','3','4','5','6','7','8','9','A','B','C','D','E','F']
    color = ""
    for i in range(6):
        color += colorArr[random.randint(0,14)]
    return "#"+color


st.set_page_config(page_title="团队人员能力差异性", page_icon="🙌")
st.sidebar.header("不同团队内不同成员在各维度的标准差情况")

#读取数据
df = pd.read_excel(os.getcwd() + '//' + 'talents.xlsx',index_col=[0])
#团队成员指标平均值
df_mean = df.iloc[:,1:].groupby('团队').mean().round(2)
#团队成员指标标准差
df_std = df.iloc[:,1:].groupby('团队').std().round(2)
df_position = pd.read_excel(os.getcwd() + '//' + 'peoples.xlsx',index_col=[0])
df_view = pd.read_excel(os.getcwd() + '//' + 'views.xlsx')

#定义雷达图维度及相应数据
df_tech = df_std[['产品设计','业务分析','产品运营','项目管理','前端开发','安全体系','网络攻防']]
#df_business = df[['权益投资','固收投资','指数投资','量化投资','合规风控','风险绩效','研究管理']]
#df_diathesis = df[['灵气','逻辑性','创新思维','价值导向','激情','情商','团队合作','承压能力','领导力']]
df_business = df_std[df_view.query('维度 == "业务知识"').loc[:,'指标'].values.tolist()]
df_diathesis = df_std[df_view.query('维度 == "通用素质"').loc[:,'指标'].values.tolist()]

#选择维度
col1, col2, col3, col4 = st.columns(4)
with col1:
   tech = st.write('请选择要展示的维度')
with col2:
   tech = st.checkbox('技术能力', value=True, key='tech_checkbox')
with col3:
   business = st.checkbox('业务知识', value=True, key='business_checkbox')
with col4:
   diathesis = st.checkbox('通用素质', value=True, key='diathesis_checkbox')


#选择人员
options = st.multiselect(
    '请选择团队',
    df_std.index.values.tolist()
    ,['投研研发3团','营销服务团']
    )
team_member = df.query('团队 in @options').loc[:,'姓名'].values.tolist()
#st.write(team_member)

#获取所选择人员对应的岗位
selected_positons = df_position.query('姓名 in @team_member').loc[:,'岗位'].drop_duplicates().dropna().values.tolist()
#获取所选择岗位对应的指标
select_views = df_view.query('维度 in @selected_positons').loc[:,'指标'].drop_duplicates().dropna().values.tolist()
#获取对应指标相应的数据
df_tech = df_std[select_views]


# 定义技术维度雷达图
radar_tech = Radar()
radar_tech.add_schema(schema=[
        {"name": col_name, "max": 3, "min": 0} 
        for col_name in df_tech.columns
    ])
radar_tech.set_global_opts(
    title_opts = opts.TitleOpts(title="技术能力维度"),
)

# 定义业务知识维度雷达图
radar_business = Radar()
radar_business.add_schema(schema=[
        {"name": col_name, "max": 3, "min": 0} 
        for col_name in df_business.columns
    ])
radar_business.set_global_opts(
    title_opts = opts.TitleOpts(title="业务知识维度"),
)

# 定义通用素质维度雷达图
radar_diathesis = Radar()
radar_diathesis.add_schema(schema=[
        {"name": col_name, "max": 3, "min": 0} 
        for col_name in df_diathesis.columns
    ])
radar_diathesis.set_global_opts(
    title_opts = opts.TitleOpts(title="通用素质维度"),
)

#添加雷达图数据
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
if tech:
    st_pyecharts(radar_tech, height="500px", key="1")
#显示业务知识维度雷达图
if business:
    st_pyecharts(radar_business, height="500px", key="2")
#显示通用素质维度雷达图
if diathesis:
    st_pyecharts(radar_diathesis, height="500px", key="3")