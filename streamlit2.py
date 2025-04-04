import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px

#FFT 累積データをstreamlitで表示する
# ファイルアップロード

f = st.file_uploader("CSVファイルをアップロードしてください", type="csv")

# ファイルがアップロードされた場合
if f is not None:
    df = pd.read_csv(f,index_col=0)
    st.write("アップロードされたデータフレーム:")
    max_value=int(df["freq"].max())
    min_value=int(df["freq"].min())

    slider=st.slider("下限範囲", min_value, max_value, min_value, 10)
    df = df[df["freq"] >= slider]
    
    slider2=st.slider("上限範囲", min_value, max_value, max_value, 10)
    df = df[df["freq"] <= slider2]

    st.scatter_chart(df,x=df["freq"],y=df["max"])