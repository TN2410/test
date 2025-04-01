#FFT 累積データをstreamlitで表示する

import streamlit as st
import pandas as pd
import os
import numpy as np


age = st.slider("ファイルを選択してください", 0, 100, 20)

st.title("データフレームの表示")

df = pd.DataFrame(
    np.random.rand(20, 3),
    columns=['Column A', 'Column B', 'Column C']
)

st.write("▼DataFrameの表示例")
st.dataframe(df)  # データフレーム表示