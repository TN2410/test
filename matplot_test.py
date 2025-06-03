#%matplotlib inline
import streamlit as st
import numpy as np
import matplotlib as plt

st.write("test")
fig=plt.figure()

x = list(range(50))
y = np.random.randn(50)

plt.plot(x, y)
plt.title('Matplotlib and Streamlit')
plt.xlabel('X-axis')
plt.ylabel('Y-axis')

# Streamlitで表示
st.pyplot(fig)