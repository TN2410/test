#FFT 累積データをstreamlitで表示する


import streamlit as st
import pandas as pd
import os

dirname = r'C:\Users\1219829\OneDrive - トヨタ自動車株式会社\○開発資料\WEC\FFT\DYNO_TEST\P0053\202503_PdSFTFr差\317_Dyno_File_0005_404_2025_HPP RH Z_accum_400.csv'
#df=pd.read_csv(dirname,encoding="CP932",skiprows=0)
age = st.slider("ファイルを選択してください", 0, 100, 20)
plt.plot(3,3)