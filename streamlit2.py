#FFT 累積データをstreamlitで表示する

import streamlit as st
import pandas as pd
import os
import numpy as np


age = st.slider("ファイルを選択してください", 0, 100, 20)

st.title("データフレームの表示")

df2 = pd.read_csv(r'C:\Users\1219829\OneDrive - トヨタ自動車株式会社\○開発資料\WEC\FFT\DYNO_TEST\P0053\202503_PdSFTFr差\317_Dyno_File_0005_404_2025_HPP RH Z_accum_400.csv')

df = pd.DataFrame(
    np.random.rand(20, 3),
    columns=['Column A', 'Column B', 'Column C']
)

st.write("▼DataFrameの表示例")
st.dataframe(df)  # データフレーム表示
st.dataframe(df2)  # データフレーム表示