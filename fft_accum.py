import os,time,gc,math,glob
import streamlit as st
import pandas as pd
import numpy as np

f = st.file_uploader("accumCSVファイルをアップロードしてください", type="csv",accept_multiple_files=True)

# ファイルがアップロードされた場合
if f is not None:
    df = pd.read_csv(f,index_col=0)#8192までがindex　#カラム名は回転数
    df=df.astype(float)
    color = st.color_picker('Pick A Color', '#00f900')

    df = df.T
    #グラフ用に振幅最大値を算出
    amax = df.max().max()#周波数と時間軸のスライダに応じて最大値を出したい
    df['Time'] = np.arange(0,int(len(df)))#時間軸は窓長さに変化する必要あり
    df['Time'] = df['Time'].astype(int)
    df["NE"] =list(df.index)
    df["NE"] = df["NE"].astype(float)
    #option = st.selectbox('日付',list(range(1, 32)))

    slider=st.slider("範囲", 0, len(df), 0, 1)
    slider2=st.slider("下限周波数", 0, 5000, 0, 100)
    slider3=st.slider("上限周波数", 0, 5000, 0, 100)

    #指定回転数の色を分ける
    st.scatter_chart(df,x='Time',y="NE",color=(60,0,255))