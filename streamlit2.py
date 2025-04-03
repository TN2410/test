import streamlit as st
import pandas as pd
import numpy as np

data = pd.DataFrame({
    'weight': np.random.normal(150, 10, 10000),
    'height': np.random.normal(100, 20,5000)
})
st.scatter_chart(data, x="weight", y="height")