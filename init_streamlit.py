# -*- coding: utf-8 -*-
import pathlib
import os
from bs4 import BeautifulSoup
from shutil import copyfile
 
from configs import ROOT_PATH
 
 
def modify_title_str(soup, title):
    """
    修改 index.html 的 title
    """
    soup.title.string = title
    return soup
 
 
def add_js_code(soup, js_code):
    """
    添加 js code 到 index.html 中
    """
    script_tag = soup.find(id='custom-js')
    if not script_tag:
        script_tag = soup.new_tag("script", id='custom-js')
    # custom-js script 中的 js code
    script_tag.string = js_code
    # 向 body 节点中添加内容
    soup.body.append(script_tag)
    return soup
 
 
def replace_favicon(streamlit_model_path):
    """替换streamlit的icon"""
    logo_path = os.path.join(streamlit_model_path, 'static', 'favicon.png')
    # 删除 logo
    pathlib.Path(logo_path).unlink()
    copyfile(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'favicon.png'), logo_path)
 
 
def init_streamlit(streamlit_model_path, title, footer):
    index_path = pathlib.Path(streamlit_model_path) / "static" / "index.html"
 
    soup = BeautifulSoup(index_path.read_text(encoding='utf-8'), features="lxml")
 
    soup = modify_title_str(soup, title)
    js_code = f'''
    document.querySelector("#MainMenu").style.visibility = 'hidden'
    document.querySelector('footer').innerHTML = '{footer}'
    '''
    soup = add_js_code(soup, js_code)
    index_path.write_text(str(soup), encoding='utf-8')
 
 
streamlit_model_path = os.path.join(ROOT_PATH, 'venv\\lib\\site-packages\\streamlit')
init_streamlit(streamlit_model_path=streamlit_model_path, title='懒编程', footer='Copyright © 2022, ayuliao Inc.')