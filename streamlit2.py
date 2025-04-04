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
    x=np.arange(0,100,1)
    y=np.arange(0,200,2)

    max_value=x.max()

    min_value=y.min()
    slider=st.slider("指定範囲", min_value, max_value, max_value, 1)

#上記スライダにて以下データをフィルタリング

    x = [x <=slider]

    plt.plot(x, y)
    plt.title('Matplotlib and Streamlit')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')

# Streamlitで表示
    st.pyplot(plt)