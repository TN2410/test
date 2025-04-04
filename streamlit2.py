import streamlit as st
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import plotly.express as px

#FFT 累積データをstreamlitで表示する
# ファイルアップロード

f = st.file_uploader("CSVファイルをアップロードしてください", type="csv")

# ファイルがアップロードされた場合
if f is not None:
    df = pd.read_csv(f,index_col=0)
    st.write("アップロードされたデータフレーム:")
    
    df = pd.DataFrame(np.arange(100).reshape(10, 10),
                  columns=['col_0', 'col_1', 'col_2', 'col_3'])

    max_value=df["col0"].max()

    min_value=df["col0"].min()
    slider=st.slider("指定範囲", min_value, max_value, max_value, 1)

#上記スライダにて以下データをフィルタリング

    df = df(df["col_0"] <=slider])

st.write(
    px.bar(df, x=df['col_0'], y=df['col_1'] ,title="sample figure",color='nation')
)



    plt.plot(x, y)
    plt.title('Matplotlib and Streamlit')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')

# Streamlitで表示
    st.pyplot(plt)