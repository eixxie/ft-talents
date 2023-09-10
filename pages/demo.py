# -*- coding: utf-8 -*-
import time,os,random
import streamlit as st
import numpy as np
import pandas as pd
from operator import index
from tokenize import Ignore
from streamlit_echarts import st_pyecharts
from pyecharts.charts import Radar,Line
from pyecharts import options as opts
from pyecharts.faker import Faker


#随机生成颜色
def randomcolor():
    colorArr = ['1','2','3','4','5','6','7','8','9','A','B','C','D','E','F']
    color = ""
    for i in range(6):
        color += colorArr[random.randint(0,14)]
    return "#"+color


st.set_page_config(page_title="Demo", page_icon="✔")

#读取数据
df = pd.read_excel(os.getcwd() + '//' + 'talents.xlsx',index_col=[0])
df_position = pd.read_excel(os.getcwd() + '//' + 'peoples.xlsx',index_col=[0])
df_view = pd.read_excel(os.getcwd() + '//' + 'views.xlsx')

pivot_team = df.pivot_table(index = '团队',columns = '灵气',values = '逻辑性',aggfunc='count',fill_value=0)

#st.write(pivot_team)
st.write(pivot_team.columns.to_list())

area_Chart = Line()
area_Chart.set_global_opts(title_opts=opts.TitleOpts(title="团队人才分布堆积图"))
area_Chart.add_xaxis(['1','2','3','4','5'])
for item in pivot_team.index:
    current_color=randomcolor()
    #st.write(pivot_team.loc[item].tolist())
    area_Chart.add_yaxis(
        item,
        pivot_team.loc[item].tolist(),
        color = current_color,
        areastyle_opts=opts.AreaStyleOpts(color = current_color,opacity=0.3),
        linestyle_opts=opts.LineStyleOpts(color = current_color,width=1),
        label_opts=opts.LabelOpts(is_show=False),
        is_smooth = True,# 平滑曲线
        stack="pileup",# 设置堆积图
    )

st_pyecharts(area_Chart, height="600px", key="2")

