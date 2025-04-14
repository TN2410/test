#FFT 累積データをstreamlitで表示する

#%matplotlib inline
import os,time,gc,math,glob
import streamlit as st
import pandas as pd
import numpy a np
import plotly.express as px
import matplotlib.pyplot as plt

#FFT 累積データをstreamlitで表示する
# ファイルアップロード

f = st.file_uploader("accumCSVファイルをアップロードしてください", type="csv")

# ファイルがアップロードされた場合
if f is not None:
    df = pd.read_csv(f,index_col=0)#8192までがindex　#カラム名は回転数
    df = df.T
    df['Time'] = np.arange(0,len(df))
    df = df.T    

    df["NE"] = df["NE"].astype(float)
    df['Time'] = df['Time'].astype(int)

    df=df.astype(float)
    print(df)
    #option = st.selectbox('日付',list(range(1, 32)))

    max_value=df['Time'].max()
    min_value=df['Time'].min()

    slider=st.slider("範囲", min_value, max_value, max_value, 10)

    df= df[df['Time'] <=slider]
    st.line_chart(df,)
    st.scatter_chart(df2,x='Time',y='NE')



    