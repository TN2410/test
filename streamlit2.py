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

    df = pd.DataFrame(np.random.rand(20, 3),columns=['a', 'b', 'c'])

    max_value=int(df['a'].max())

    min_value=int(df['a'].min())
    slider=st.slider("指定範囲", min_value, max_value, max_value, 1)

    st.line_chart(df)


#上記スライダにて以下データをフィルタリング

    df = df[df['a'] <=slider]
    st.line_chart(df)
