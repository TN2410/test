#FFT 累積データをstreamlitで表示する
# ファイルアップロード

#%matplotlib inline
import os,time,gc,math,glob
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt

#FFT 累積データをstreamlitで表示する
# ファイルアップロード

f = st.file_uploader("txtファイルをアップロードしてください", type="txt")
#f=r"C:\Users\1219829\Desktop\python\streamlit\ff.csv"
rpm=[]
# ファイルがアップロードされた場合
if f is not None:
    df = pd.read_csv(f,sep="[\t\0]",index_col=0)
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
    plt.title("testtest")
    plt.xlabel('X-axis')  
    plt.ylabel('Y-axis')

# Streamlitで表示
    st.pyplot(plt)