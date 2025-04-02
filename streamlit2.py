#FFT 累積データをstreamlitで表示する

import os
import streamlit as st
import pandas as pd

dirname = r'C:\Users\1219829\Desktop\python\streamlit\317_Dyno_File_0003_404_520wk_HPP LH X_accum_400.csv'

if os.path.exists(dirname):
	df = pd.read_csv(dirname, encoding="utf-8", skiprows=0)
	print(df.columns)
	st.title("exist data")
	age = st.slider("ファイルを選択してください",0,40,20)
else:
	st.title("not exist data")
	age = st.slider("ファイルを選択してください",0,800,20)
	age = st.slider("ファイルを選択してください",0,100,20)