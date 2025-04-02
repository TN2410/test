#FFT 累積データをstreamlitで表示する

import os
import streamlit as st
import pandas as pd

filename="C:\Users\1219829\Desktop\python\streamlit\317_Dyno_File_0003_404_520wk_HPP LH X_accum_400.csv"

df = pd.read_csv(filename, encoding='utf-8', skiprows=0)
#st.dataframe(df.columns)
	
st.title("filename")
age = st.slider("ファイルを選択してください",0,40,20)

age = st.slider("ファイルを選択してください",0,800,20)
age = st.slider("ファイルを選択してください",0,100,20)