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

    Random = np.random.randint(low=0, high=100, size=(row, cols))

    df = pd.DataFrame(Random)
    
    max_value=int(df['1'].max())

    min_value=int(df['1'].min())
    slider=st.slider("指定範囲", min_value, max_value, max_value, 1)

    st.line_chart(df)


#上記スライダにて以下データをフィルタリング

    df = df[df['1'] <=slider]
    st.line_chart(df)
