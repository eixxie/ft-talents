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


#随机生成颜色
def randomcolor():
    colorArr = ['1','2','3','4','5','6','7','8','9','A','B','C','D','E','F']
    color = ""
    for i in range(6):
        color += colorArr[random.randint(0,14)]
    return "#"+color


st.set_page_config(page_title="按评估指标看人员", page_icon="💢",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    })
st.sidebar.header("不同指标下的专业人员")

#读取数据
df = pd.read_excel(os.getcwd() + '//' + 'talents.xlsx',index_col=[0])
df_position = pd.read_excel(os.getcwd() + '//' + 'peoples.xlsx',index_col=[0])
df_view = pd.read_excel(os.getcwd() + '//' + 'views.xlsx')

#定义雷达图维度及相应数据
df_tech = df[['产品设计','业务分析','产品运营','项目管理','前端开发','安全体系','网络攻防']]
#df_business = df[['权益投资','固收投资','指数投资','量化投资','合规风控','风险绩效','研究管理']]
#df_diathesis = df[['灵气','逻辑性','创新思维','价值导向','激情','情商','团队合作','承压能力','领导力']]
df_business = df[df_view.query('维度 == "业务知识"').loc[:,'指标'].values.tolist()]
df_diathesis = df[df_view.query('维度 == "通用素质"').loc[:,'指标'].values.tolist()]

#选择各维度关注的指标
#title = st.write('请选择查询指标')
view_col1, view_col2 = st.columns(2)
with view_col1:
   #选择阈值
    options_value = st.multiselect(
        '得分阈值',
        ['5','4','3','2','1'],['4'],max_selections=1,
        key = 'value_mselect'
    )
with view_col2:
   st.write('筛选小于等于阈值的情况')
   tech_checkbox = st.checkbox('小于等于', value=False,help='如不选择此项，则默认筛选大于等于阈值的情况', key='tech_checkbox')

#选择技术能力指标
options_tech = st.multiselect(
    '技术能力指标',
    df_view.query('维度 == "技术能力"').loc[:,'指标'].values.tolist(),
    key = 'tech_mselect'
)
#选择业务知识指标
options_business = st.multiselect(
    '业务知识指标',
    df_view.query('维度 == "业务知识"').loc[:,'指标'].values.tolist(),
    key = 'business_mselect'
)
#选择基础素质指标
options_diathesis = st.multiselect(
    '基础素质指标',
    df_view.query('维度 == "通用素质"').loc[:,'指标'].values.tolist(),
    key = 'diathesis_mselect'
)

#将查询条件进行组合
options = options_tech + options_business + options_diathesis
#st.write(options)

#查询所选择的维度均大于3的人员
query_string = ""
compare_type = ''
compare_type='<=' if tech_checkbox  else '>='
for item in options:
    query_string += item + compare_type + "".join(options_value) +' & ' 
#st.write(query_string[:-2])


#按照查询结果中每行记录的平均值从大到小排序
#st.write(df.query('灵气 >3 & 逻辑性 >3').loc[:,options])
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