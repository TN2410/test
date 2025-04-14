#FFT 累積データをフォルダ選択で自動計算する

#%matplotlib inline
import os,time,gc,math,glob
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt

# ファイルアップロード
f = st.file_uploader("txtファイルをアップロードしてください", type="txt")
#f=r"C:\Users\1219829\Desktop\python\streamlit\ff.csv"
# ファイルがアップロードされた場合
if f is not None:
#フォルダ名とチェックボックスを表示
    df = pd.read_csv(f,sep="[\t\0]",index_col=0)
    selected_data = df[st.multiselect('列を選択してください', df.columns)]
    st.line_chart(selected_data)
#smpファイルよりチェックRAM名を読み取り
#結果表示
    df["NE"][1:] = df["NE"][1:].astype(int)

    max_value = df["NE"][1:].max()
    min_value = df["NE"][1:].min()

    df["Time"] = np.arange(len(df))
    st.scatter_chart(df,x="Time",y="NE")

    slider=st.slider("範囲", min_value, max_value, max_value, 10)
    df["Time"]=np.arange(len(df)).astype(float)
    x=df["Time"][1:]
    y=df["NE"][1:]
#    print(slider)

    plt.plot(x, y)
    plt.ylim(min_value, max_value)

    plt.title("testtest")
    plt.xlabel('X-axis')  
    plt.ylabel('Y-axis')

# Streamlitで表示
    st.pyplot(plt)
