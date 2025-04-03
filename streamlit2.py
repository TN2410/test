import streamlit as st
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

#FFT 累積データをstreamlitで表示する
# ファイルアップロード

f = st.file_uploader("CSVファイルをアップロードしてください", type="csv")

# ファイルがアップロードされた場合
if f is not None:
    df = pd.read_csv(f,index_col=0)
    st.write("アップロードされたデータフレーム:")
    st.write(df)

    # matplotlibで図を用意する
    time=np.arrange(0,len(df.columns),1)
    plt.plot(time, df.columns, marker='.', markersize=10)
    #plt.xlim(0.5, 12.5)
    #plt.ylim(0, 40)
    plt.title('Average Temperature at Kyoto in 2018', fontsize=15)
    plt.xlabel('month', fontsize=10)
    plt.ylabel('average temperature (deg)', fontsize=10)

    # streamlit plot
    st.pyplot(fig)




    age = st.slider("ファイルを選択してください",0,800,20)
    age = st.slider("ファイルを選択してください",0,100,20)
