import streamlit as st
import pandas as pd
import numpy as np

data = pd.DataFrame({
    'weight': np.random.normal(150, 10, 10000),
    'height': np.random.normal(100, 50,10000)
})
st.scatter_chart(data, x="weight", y="height")

#FFT 累積データをstreamlitで表示する



# ファイルアップロード
uploaded_file = st.file_uploader("CSVファイルをアップロードしてください", type="csv")

# ファイルがアップロードされた場合
if uploaded_file is not None:
   	df = pd.read_csv(uploaded_file)
   	st.write("アップロードされたデータフレーム:")
	st.write(df)




st.title("not exist data")
age = st.slider("ファイルを選択してください",0,800,20)
age = st.slider("ファイルを選択してください",0,100,20)