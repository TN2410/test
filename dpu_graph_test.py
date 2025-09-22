import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.title("Plotlyテスト用ヒストグラム")

# テスト用のデータ生成
np.random.seed(0)
data = np.random.randn(500)

# ヒストグラム作成
fig = go.Figure(
    data=[go.Histogram(x=data, nbinsx=30, marker_color='navy', opacity=0.7)]
)

fig.update_layout(
    title="ランダム正規分布データのヒストグラム",
    xaxis_title="値",
    yaxis_title="度数",
    template="simple_white"
)

st.plotly_chart(fig, use_container_width=True)