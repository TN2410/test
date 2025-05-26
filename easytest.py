import sys
sys.path.append(r'c:\users\1219829\python\py38\lib\site-packages')
sys.path.append(r'C:\Users\1219829\python\Py38\Scripts')
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.write("test")

x = list(range(50))
y = np.random.randn(50)

plt.plot(x, y)
plt.title('Matplotlib and Streamlit')
plt.xlabel('X-axis')
plt.ylabel('Y-axis')

# Streamlitで表示
st.pyplot(plt)