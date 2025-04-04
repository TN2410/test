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
    
    df = pd.DataFrame(data={'col_0': np.arange(0,100,1), 'col_1': np.arange(0,200,2)})

    max_value=df['col0'].max()

    min_value=df['col0'].min()
    slider=st.slider("指定範囲", min_value, max_value, max_value, 1)

#上記スライダにて以下データをフィルタリング

    df = df[df['col_0'] <=slider]
    st.write(df)
st.write(
    px.bar(df, x=df['col_0'], y=df['col_1'] ,title='sample figure')
)


'