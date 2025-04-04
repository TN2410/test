import streamlit as st
import pandas as pd
import numpy as np
import os


#FFT 累積データをstreamlitで表示する
# ファイルアップロード

f = st.file_uploader("CSVファイルをアップロードしてください", type="csv")

# ファイルがアップロードされた場合
if f is not None:
    df = pd.read_csv(f,index_col=0)
    
    st.title(df.iloc[1,1] )
    st.write("アップロードされたデータフレーム:")
    st.write(df)

    time=np.arange(0,8192,1)

    st.scatter_chart(df,x="freq",y="max")	

    #plt.xlim(0.5, 12.5)
    #plt.ylim(0, 40)

    age = st.slider("ファイルを選択してください",0,800,20)
    age = st.slider("ファイルを選択してください",0,100,20)