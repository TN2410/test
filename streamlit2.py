#FFT 累積データをstreamlitで表示する

import os
import streamlit as st
import pandas as pd
import numpy as np


filename=r"C:\Users\1219829\Desktop\python\streamlit\317_Dyno_File_0003_404_520wk_HPP LH X_accum_400.csv"

data = pd.DataFrame({
    'weight': np.random.normal(150, 10, 100),
    'height': np.random.normal(50, 5, 100)
})
st.scatter_chart(data, x="weight", y="height")

#df = pd.read_csv(filename, encoding='utf-8', skiprows=0)
#st.dataframe(df.columns)
	
st.title("filename")
age = st.slider("ファイルを選択してください",0,40,20)

age = st.slider("ファイルを選択してください",0,800,20)
age = st.slider("ファイルを選択してください",0,100,20)


# ファイルアップローダーの準備
uploaded_file = st.file_uploader(r"C:\Users\1219829\Desktop\python\streamlit\317_Dyno_File_0003_404_520wk_HPP LH X_accum_400.csv", type="csv")

# uploadファイルが存在するときだけ、csvファイルの読み込みがされる。
if uploaded_file is not None:
    # データファイルの読み込み
    df = pd.read_csv(uploaded_file , encoding="utf-8")
    st.scatter_chart(df, x=df["freq"], y=df["max"])

    # streamlit plot

 
    st.write(f'中央値：{median}')
    st.write(f'平均値：{mean}')