# -*- coding: utf-8 -*-
from pickle import NONE
import time,os,random
from turtle import position
import streamlit as st
import numpy as np
import pandas as pd
from operator import index
from tokenize import Ignore
from streamlit_echarts import st_pyecharts
from pyecharts.charts import Radar,Line,Scatter
from pyecharts.commons.utils import JsCode
from pyecharts import options as opts
from PIL import Image
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
st.set_page_config(page_title="人才地图", page_icon="✨",layout="wide")
st.sidebar.header("Question:\n 谁是超级明星？谁是潜力之星？谁是待发展者？谁是中坚力量？谁是问题员工？")

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
st.header('人才地图')
st.caption('📌可以选择一个或若干个团队 或 某个岗位，从而查看相应人员在人才地图（横轴是通用素质得分、纵轴是绩效得分）上的分布情况。')
st.divider()
#读取数据
df = pd.read_excel(os.getcwd() + '//' + 'talents.xlsx',index_col=[0])
df_position = pd.read_excel(os.getcwd() + '//' + 'peoples.xlsx',index_col=[0])
df_view = pd.read_excel(os.getcwd() + '//' + 'views.xlsx')

#定义雷达图维度及相应数据
df_business = df[df_view.query('维度 == "业务知识"').loc[:,'指标'].values.tolist()]
df_diathesis = df[df_view.query('维度 == "通用素质"').loc[:,'指标'].values.tolist()]
df['business'] = df[df_view.query('维度 == "业务知识"').loc[:,'指标'].values.tolist()].mean(axis=1)
df['diathesis'] = df[df_view.query('维度 == "通用素质"').loc[:,'指标'].values.tolist()].mean(axis=1)

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
#获取对应指标相应的数据
df_tech = df[select_views]
df['tech'] = df[select_views].mean(axis=1)


if view_type == '按团队' and len(options_team)==0:
    df_potential = df.loc[:,['姓名','diathesis','绩效2022']].query('绩效2022 > 1')
    df_mirgate = df.loc[:,['姓名','绩效2021','绩效2022']].query('绩效2021 > 1 & 绩效2022 > 1')
else:
    df_potential = df.loc[team_member,['姓名','diathesis','绩效2022']].query('绩效2022 > 1')
    df_mirgate = df.loc[team_member,['姓名','绩效2021','绩效2022']].query('绩效2021 > 1 & 绩效2022 > 1')
#st.write(df_potential)
#定义九宫格气泡图
popo_Chart = Scatter()
popo_Chart.set_global_opts(#全局变量 
    title_opts=opts.TitleOpts(title="人才分布地图"),#设置标题 
    tooltip_opts=opts.TooltipOpts(#Js代码控制气泡弹窗提示文字
        formatter=JsCode(
            "function (params) {return params.value[2]+ '\n 通用素质：'+params.value[0] + '\n 2022绩效：'+params.value[1]}" 
        ) 
    ),
    visualmap_opts=opts.VisualMapOpts(#控制气泡大小 
        type_="size", max_=0.5, min_=0.5, dimension=0.1),
    xaxis_opts=opts.AxisOpts(min_=3,max_=5,name='通用素质'),#设置X轴起始值，X轴名字 
    yaxis_opts=opts.AxisOpts(min_=3,max_=5,name = '2022绩效'),#设置Y轴起始值，Y轴名字
)
popo_Chart.add_xaxis(df_potential.diathesis)#添加x轴数据
popo_Chart.add_yaxis(#添加y轴数据
    '2022绩效', 
    [list(z) for z in zip(df_potential.绩效2022, df_potential.姓名)],#Y轴数据，岗位，城市
    label_opts=opts.LabelOpts(#Js代码控制气泡显示提示文字
        formatter=JsCode(
            "function(params){return params.value[2]}" #提示
            )
    ),
    itemstyle_opts=opts.ItemStyleOpts(color='#1EB9E1'),
)

#定义绩效关系气泡图
mirgate_Chart = Scatter()
mirgate_Chart.set_global_opts(#全局变量 
    title_opts=opts.TitleOpts(title="人才绩效迁移地图"),#设置标题 
    tooltip_opts=opts.TooltipOpts(#Js代码控制气泡弹窗提示文字
        formatter=JsCode(
            "function (params) {return params.value[2]+ '\n 2021绩效：'+params.value[0] + '\n 2022绩效：'+params.value[1]}" 
        ) 
    ),
    visualmap_opts=opts.VisualMapOpts(#控制气泡大小 
        type_="size", max_=0.5, min_=0.5, dimension=0.1),
    xaxis_opts=opts.AxisOpts(min_=3,max_=5,name='2021绩效'),#设置X轴起始值，X轴名字 
    yaxis_opts=opts.AxisOpts(min_=3,max_=5,name = '2022绩效'),#设置Y轴起始值，Y轴名字
)
mirgate_Chart.add_xaxis(df_mirgate.绩效2021)#添加x轴数据
mirgate_Chart.add_yaxis(#添加y轴数据
    '2022绩效', 
    [list(z) for z in zip(df_mirgate.绩效2022, df_mirgate.姓名)],#Y轴数据，岗位，城市
    label_opts=opts.LabelOpts(#Js代码控制气泡显示提示文字
        formatter=JsCode(
            "function(params){return params.value[2]}" #提示
            )
    ),
    itemstyle_opts=opts.ItemStyleOpts(color='#f8ac59'),
)

#展示气泡图
st_pyecharts(popo_Chart, height="600px", key="1")
st.divider()
st_pyecharts(mirgate_Chart, height="600px", key="2")

#展示参考信息
st.divider()
st.write('说明：一般使用九宫格地图来盘点人才，不仅显示单个人才在组织中的位置，也显示了团队的整体情况')
image = Image.open(os.getcwd() + '//' + 'talents_map2.png')
st.image(image, caption='人才地图九宫格')