#FFT 累積データをstreamlitで表示する

import os
import streamlit as st
import pandas as pd
import os

dirname = r'C:\Users\1219829\desktop\python\streamlit\317_Dyno_File_0003_404_520wk_HPP LH X_accum_400.csv'

if os.path.exists(dirname):
	df = pd.read_csv(dirname, encoding="utf-8", skiprows=0)
	print(df)
else:
	print("File does not exist!")

age = st.slider("ファイルを選択してください", 0, 100, 20)
