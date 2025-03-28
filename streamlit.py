import sys
import numpy as np
import pandas as pd

sys.path.append(r'c:\users\1219829\python\py38\lib\site-packages')
sys.path.append(r'C:\Users\1219829\python\Py38\Scripts')
sys.path.append(r'C:\Users\1219829\AppData\Local\Programs\Python\Python312\Scripts')

import streamlit as st

df=pd.DataFrame(np.random.rand(100,2)/[20,20]+[35.19,138.80],columns=["lat","lon"])

st.text("test")
st.slider("testrrrst",0,50,100)
st.map(df)