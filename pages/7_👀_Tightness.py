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


#随机生成颜色
def randomcolor():
    colorArr = ['1','2','3','4','5','6','7','8','9','A','B','C','D','E','F']
    color = ""
    for i in range(6):
        color += colorArr[random.randint(0,14)]
    return "#"+color


st.set_page_config(page_title="团队松紧度分析", page_icon="🤼‍♂️")
st.sidebar.header("不同团队的松紧度情况")

#读取数据
df = pd.read_excel(os.getcwd() + '//' + 'talents.xlsx',index_col=[0])
df_view = pd.read_excel(os.getcwd() + '//' + 'views.xlsx')

#定义雷达图维度及相应数据
df_tech = df[['产品设计','业务分析','产品运营','项目管理','前端开发','安全体系','网络攻防']]
#df_business = df[['权益投资','固收投资','指数投资','量化投资','合规风控','风险绩效','研究管理']]
#df_diathesis = df[['灵气','逻辑性','创新思维','价值导向','激情','情商','团队合作','承压能力','领导力']]
df_business = df[df_view.query('维度 == "业务知识"').loc[:,'指标'].values.tolist()]
df_diathesis = df[df_view.query('维度 == "通用素质"').loc[:,'指标'].values.tolist()]

#选择基础素质指标
options_diathesis = st.multiselect(
    '基础素质指标',
    df_view.query('维度 == "通用素质"').loc[:,'指标'].values.tolist(),
    ['灵气'],
    max_selections=1,
    key = 'diathesis_mselect'
)

#选择团队
options_team = st.multiselect(
    '请选择团队',
    df.iloc[:, 1].drop_duplicates().dropna().values.tolist(),
    ['投研研发3团','营销服务团']
)

#如果选择了基础素质指标，则展示信息，否则不展示
if len(options_diathesis)!=0:
    #如果未选择团队，则统计整体情况，否则统计相应团队的情况
    if len(options_team) == 0:
        pivot_team = df.pivot_table(columns = "".join(options_diathesis),values = '分级',aggfunc='count',fill_value=0) 
    else:
        pivot_team = df.pivot_table(index = '团队',columns = "".join(options_diathesis),values = '分级',aggfunc='count',fill_value=0) \
                        .query('团队 in @options_team')
    #统计各个评分项的百分比信息，如果统计信息缺列，则自动补0
    for item in list(set([1,2,3,4,5]).difference(set(pivot_team.columns.tolist()))):
        pivot_team[item] = '0'
    #st.write(pivot_team)
    #将数量统计转化为百分比
    pivot_team = pivot_team.loc[:,[1,2,3,4,5]].div(pivot_team.sum(axis=1), axis=0).round(2)

    #st.write(pivot_team)
    #st.write(pivot_team.columns.to_list())

    #定义面积堆叠图
    area_Chart = Line()
    area_Chart.set_global_opts(title_opts=opts.TitleOpts(title="团队评分分布图"))
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

