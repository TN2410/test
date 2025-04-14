#FFT 累積データをstreamlitで表示する

#%matplotlib inline
import os,time,gc,math,glob
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt

#FFT 累積データをstreamlitで表示する
# ファイルアップロード

f = st.file_uploader("accumCSVファイルをアップロードしてください", type="csv")

# ファイルがアップロードされた場合
if f is not None:
    df = pd.read_csv(f,index_col=0)#8192までがindex　#カラム名は回転数
    df=df.astype(float)
    color = st.color_picker('Pick A Color', '#00f900')

    df = df.T
    df['Time'] = np.arange(0,len(df))
    df['Time'] = df['Time'].astype(int)
    df["NE"] =list(df.index)
    df["NE"] = df["NE"].astype(float)
    #option = st.selectbox('日付',list(range(1, 32)))

    slider=st.slider("範囲", 0, len(df), 0, 1)
    #指定回転数の色を分ける
    st.scatter_chart(df,x='Time',y="NE",color=(60,0,255))

    plt.plot(df["NE"],df["Time"])

    #plt.plot(df.columns[:-2].tolist(),df.iloc[slider,:-2].tolist())
    fig = plt.figure()
    plt.xlim(-8200, 0)
    
    st.pyplot(fig)