# -*- coding: utf-8 -*-
from pickle import NONE
import time,os,random
import streamlit as st
import numpy as np
import pandas as pd
from operator import index
from tokenize import Ignore
from streamlit_echarts import st_pyecharts
from pyecharts.charts import Boxplot
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
st.set_page_config(page_title="能力分布分析", page_icon="✨",layout="wide")
st.sidebar.header("Question:\n 我们在各个能力项上的能力分布如何？")

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
st.header('能力分布分析')
st.caption('📌可以选择一个或若干个团队 或 某个岗位，从而查看相应人员在各项能力上的分布情况（最高、75分位、中位数、25分位、最低水平）。')
st.divider()
#读取数据
df = pd.read_excel(os.getcwd() + '//' + 'talents.xlsx',index_col=[0])
df_position = pd.read_excel(os.getcwd() + '//' + 'peoples.xlsx',index_col=[0])
df_view = pd.read_excel(os.getcwd() + '//' + 'views.xlsx')

#定义雷达图维度及相应数据
df_tech = df[df_view.query('维度 == "技术能力"').loc[:,'指标'].values.tolist()]
df_business = df[df_view.query('维度 == "业务知识"').loc[:,'指标'].values.tolist()]
df_diathesis = df[df_view.query('维度 == "通用素质"').loc[:,'指标'].values.tolist()]

#选择维度
view_col1, view_col2, view_col3 = st.columns([1,1,2])
with view_col1:
    view_type = st.radio("查看范围：",['按岗位','按团队'])
with view_col2:
    option_pos = st.selectbox(
        '请选择岗位：',
        df_position.iloc[:, 1].drop_duplicates().dropna().values.tolist(),key = 'positon_select')
with view_col3:
    #选择团队
    options_team = st.multiselect(
        '请选择团队：',
        df.iloc[:, 1].drop_duplicates().dropna().values.tolist(),
        ['投研研发3团','营销服务团']
    )

#取得岗位或团队中的人员
if view_type == '按岗位':
    team_member = df_position.query('岗位 in @option_pos').loc[:,'姓名'].values.tolist()
else:
    team_member = df.query('团队 in @options_team').loc[:,'姓名'].values.tolist()
#st.write(team_member)

#获取所选择人员对应的岗位
selected_positons = df_position.query('姓名 in @team_member').loc[:,'岗位'].drop_duplicates().dropna().values.tolist()
#获取所选择岗位对应的指标
select_views = df_view.query('维度 in @selected_positons').loc[:,'指标'].drop_duplicates().dropna().values.tolist()

#如果选择了团队，则只显示相应团队的人的情况，否则显示所有人的情况
if view_type != '按团队' or len(options_team)!=0:
    df_tech = df_tech.loc[team_member]
    df_business = df_business.loc[team_member]
    df_diathesis = df_diathesis.loc[team_member]

#人数小于3个时，无法展示
if len(df_tech) <3:
    st.write("人数少于3个，无法展示分布情况")
    st.stop()
#定义技术能力分布箱体图
tech_box = Boxplot()
tech_box.add_xaxis(list(df_tech))
tech_box.add_yaxis("评分", 
            tech_box.prepare_data(df_tech.T.values.tolist()),
            itemstyle_opts=opts.ItemStyleOpts(color='#1EB9E1',border_color='#005096'),
            )
tech_box.set_global_opts(
    title_opts=opts.TitleOpts(title="技术能力分位图"),
    legend_opts=opts.LegendOpts(pos_top="3%"),
    tooltip_opts=opts.TooltipOpts(trigger="item", axis_pointer_type="shadow"),
    xaxis_opts=opts.AxisOpts(
            type_="category",
            boundary_gap=True,
            splitarea_opts=opts.SplitAreaOpts(is_show=True,areastyle_opts=opts.AreaStyleOpts(opacity=0.3)),
            splitline_opts=opts.SplitLineOpts(is_show=True),
        ),
    yaxis_opts=opts.AxisOpts(
            type_="value",
            #name="评分",
            min_ = 0.5,
            max_ = 5.5,
            splitarea_opts=opts.SplitAreaOpts(
                is_show=False, areastyle_opts=opts.AreaStyleOpts(opacity=1)
            ),
        ),
    datazoom_opts=[
        opts.DataZoomOpts(type_="inside", range_start=0, range_end=100),
        opts.DataZoomOpts(type_="slider", xaxis_index=0, is_show=True),
    ],
    )

#定义业务知识分布箱体图
business_box = Boxplot()
business_box.add_xaxis(list(df_business))
business_box.add_yaxis("评分", 
            business_box.prepare_data(df_business.values.T.tolist()),
            itemstyle_opts=opts.ItemStyleOpts(color='#1EB9E1',border_color='#005096'),
            )
business_box.set_global_opts(
    title_opts=opts.TitleOpts(title="业务知识分位图"),
    legend_opts=opts.LegendOpts(pos_top="3%"),
    tooltip_opts=opts.TooltipOpts(trigger="item", axis_pointer_type="shadow"),
    xaxis_opts=opts.AxisOpts(
            type_="category",
            boundary_gap=True,
            splitarea_opts=opts.SplitAreaOpts(is_show=True,areastyle_opts=opts.AreaStyleOpts(opacity=0.3)),
            splitline_opts=opts.SplitLineOpts(is_show=True),
        ),
    yaxis_opts=opts.AxisOpts(
            type_="value",
            #name="评分",
            min_ = 0.5,
            max_ = 5.5,
            splitarea_opts=opts.SplitAreaOpts(
                is_show=False, areastyle_opts=opts.AreaStyleOpts(opacity=1)
            ),
        ),
    datazoom_opts=[
        opts.DataZoomOpts(type_="inside", range_start=0, range_end=100),
        opts.DataZoomOpts(type_="slider", xaxis_index=0, is_show=True),
    ],
    )

#定义通用素质分布箱体图
diathesis_box = Boxplot()
diathesis_box.add_xaxis(list(df_diathesis))
diathesis_box.add_yaxis("评分", 
            diathesis_box.prepare_data(df_diathesis.T.values.tolist()),
            itemstyle_opts=opts.ItemStyleOpts(color='#1EB9E1',border_color='#005096'),
            )
diathesis_box.set_global_opts(
    title_opts=opts.TitleOpts(title="通用素质分位图"),
    legend_opts=opts.LegendOpts(pos_top="3%"),
    tooltip_opts=opts.TooltipOpts(trigger="item", axis_pointer_type="shadow"),
    xaxis_opts=opts.AxisOpts(
            type_="category",
            boundary_gap=True,
            splitarea_opts=opts.SplitAreaOpts(is_show=True,areastyle_opts=opts.AreaStyleOpts(opacity=0.3)),
            splitline_opts=opts.SplitLineOpts(is_show=True),
        ),
    yaxis_opts=opts.AxisOpts(
            type_="value",
            #name="评分",
            min_ = 0.5,
            max_ = 5.5,
            splitarea_opts=opts.SplitAreaOpts(
                is_show=False, areastyle_opts=opts.AreaStyleOpts(opacity=1)
            ),
        ),
    datazoom_opts=[
        opts.DataZoomOpts(type_="inside", range_start=0, range_end=100),
        opts.DataZoomOpts(type_="slider", xaxis_index=0, is_show=True),
    ],
    )

#展示箱体图
st_pyecharts(tech_box, height="600px", key="1")
st.divider()
st_pyecharts(business_box, height="600px", key="2")
st.divider()
st_pyecharts(diathesis_box, height="600px", key="3")