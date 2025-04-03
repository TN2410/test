import streamlit as st
import pandas as pd
import numpy as np

data = pd.DataFrame({
    'weight': np.random.normal(150, 10, 100),
    'height': np.random.normal(50, 5, 100)})
st.scatter_chart(data, x="weight", y="height")