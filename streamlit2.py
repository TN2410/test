import streamlit as st
import pandas as pd
import numpy as np

data = pd.DataFrame({
    'weight': np.random.normal(150, 10, 10000),
    'height': np.random.normal(100, 50,10000)
})
st.scatter_chart(data, x="weight", y="height")

#FFT 累積データをstreamlitで表示する

import os
import streamlit as st
import pandas as pd

dirname = r'C:\Users\1219829\Desktop\python\streamlit\ff.csv'

if os.path.exists(dirname):
	df = pd.read_csv(dirname, encoding="utf-8", skiprows=0)
	print(df.columns)
	st.title("exist data")
	age = st.slider("ファイルを選択してください",0,40,20)
else:
	st.title("not exist data")
	age = st.slider("ファイルを選択してください",0,800,20)
	age = st.slider("ファイルを選択してください",0,100,20)