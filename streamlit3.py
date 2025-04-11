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

f = st.file_uploader("txtファイルをアップロードしてください", type="txt")
#f=r"C:\Users\1219829\Desktop\python\streamlit\ff.csv"
rpm=[]
# ファイルがアップロードされた場合
if f is not None:
    df = pd.read_csv(f,sep="[\t\0]",index_col=0)
#    slider=st.slider("範囲", min_value, max_value, max_value, 10)
    st.scatter_chart(df,x='Time',y='NE')
    print(slider)
