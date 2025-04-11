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

f = st.file_uploader("accumCSVファイルをアップロードしてください", type="csv")
#f=r"C:\Users\1219829\Desktop\python\streamlit\ff.csv"
rpm=[]
# ファイルがアップロードされた場合
if f is not None:
    df = pd.read_csv(f,index_col=0)
    df=df.T

    df['Time'] = np.arange(0,len(df))
    df['NE'] = df.index.tolist()
    df["NE"][1:] = df["NE"][1:].astype(float)
    df['Time'] = df['Time'].astype(int)

    df=df.astype(float)

    max_value=df['Time'].max()
    min_value=df['Time'].min()

    slider=st.slider("範囲", min_value, max_value, max_value, 10)

    df= df[df['Time'] <=slider]
    st.line_chart(df)
    #st.scatter_chart(df,x='Time',y='NE')
    