%matplotlib inline
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.write("test")

x = list(range(50))
y = np.random.randn(50)

# plt.plot(x, y)
# plt.title('Matplotlib and Streamlit')
# plt.xlabel('X-axis')
# plt.ylabel('Y-axis')

# Streamlitで表示
# st.pyplot(plt)