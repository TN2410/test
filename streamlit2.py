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

    df.loc['time'] = np.arange(0,len(df.columns))

 
    st.scatter_chart(df,y=df.columns.tolist())
    st.write("アップロードされたデータフレーム:")
    #slider=st.slider("下限範囲", min_value, max_value, max_value, 1)
    #df = df[df["freq"] <= slider]
    #st.write(df)
#    slider2=st.slider("上限範囲", min_value, max_value, max_value, 1)
#    df2 = df[df["freq"] <= slider2]
#    st.scatter_chart(df2,x=df2["freq"],y=df2["max"])