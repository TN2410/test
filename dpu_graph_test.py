import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.write("Hello Streamlit and Plotly")

fig = go.Figure(go.Bar(y=[2, 1, 3]))
st.plotly_chart(fig)