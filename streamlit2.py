import streamlit as st
import pandas as pd
import numpy as np
import os


#FFT 累積データをstreamlitで表示する
# ファイルアップロード

f = st.file_uploader("CSVファイルをアップロードしてください", type="csv")

# ファイルがアップロードされた場合
if uploaded_file is not None:
    df = pd.read_csv(f,index_col=0)
    filename= os.path.basename(f)
    filename_no_extension = os.path.splitext(filename)[0]
    st.write("アップロードされたデータフレーム:")
    st.write(df)
    st.title(filename_no_extension)

    age = st.slider("ファイルを選択してください",0,800,20)
    age = st.slider("ファイルを選択してください",0,100,20)
