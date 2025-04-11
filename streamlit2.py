#FFT 累積データをstreamlitで表示する
# ファイルアップロード

#%matplotlib inline
import os,time,gc,math,glob
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

#FFT 累積データをstreamlitで表示する
# ファイルアップロード

f = st.file_uploader("CSVファイルをアップロードしてください", type="csv")
#f=r"C:\Users\1219829\Desktop\python\streamlit\ff.csv"
rpm=[]
# ファイルがアップロードされた場合
if f is not None:
    df = pd.read_csv(f,index_col=0)
    df=df.T

    df['time'] = np.arange(0,len(df))
    df['ne'] = df.index.tolist()
    df['ne'] = df['ne'].astype(float)
    print(df['ne'])

    max_value=df['ne'].max()
    min_value=df['ne'].min()

    st.scatter_chart(df,x='time',y='ne')
    st.write("アップロードされたデータフレーム:")
    slider=st.slider("範囲", min_value, max_value, max_value, 1)