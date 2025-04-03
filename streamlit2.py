import streamlit as st
import pandas as pd
import numpy as np

data = pd.DataFrame({
    'weight': np.random.normal(150, 10, 500),
    'height': np.random.normal(1000, 5, 500)
})
st.scatter_chart(data, x="weight", y="height")