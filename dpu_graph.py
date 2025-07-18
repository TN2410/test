# dpuデータをstreamlitで表示する
import os
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats

st.set_page_config(
    page_title="PLOT",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("windarab or dpu 積算データ")

@st.cache_data
def load_uploaded_file(uploaded_file, skiprows):
    return pd.read_csv(uploaded_file, sep="[\t\0]", skiprows=skiprows, engine="python")

def process_files(uploaded_files, specific_string):
    dataframes = {}
    for uploaded_file in uploaded_files:
        initial_lines = pd.read_csv(uploaded_file, nrows=2)
        uploaded_file.seek(0)
        skiprows = 5 if initial_lines.apply(lambda x: x.astype(str).str.contains(specific_string).any(), axis=1).any() else 2
        df = pd.read_csv(uploaded_file, sep="[\t\0]", skiprows=skiprows, engine="python")
        dataframes[uploaded_file.name] = df
    return dataframes, skiprows

def create_fig(dataframes, x_pal, y_pal, x_lower_bound, x_upper_bound, y_lower_bound, y_upper_bound, x_div_num, y_div_num):
    total_counts = {}
    z_sum = {}
    fig = make_subplots(
        rows=1,
        cols=2,
        specs=[[{"type": "surface"}, {"type": "scatter"}]],
        subplot_titles=("時間頻度", "Scatter Plot"),
        horizontal_spacing=0.1
    )

    for filename, df in dataframes.items():
        if df.empty:
            st.warning(f"{filename} は空のファイルです。")
            continue

        if "Time" in df.columns:
            df = df.iloc[1:]  # DPUの場合は単位行を除外
            time_format = "%H:%M:%S.%f"
            df["Time"] = [datetime.strptime(time_str, time_format) for time_str in df["Time"]]
            init_time = df["Time"].iloc[0]
            df["Time"] = [(time - init_time).seconds for time in df["Time"]]
            df = df.apply(pd.to_numeric, errors='coerce')

        fig.add_trace(go.Scatter(x=df[x_pal], y=df[y_pal], mode='markers', name=filename), row=1, col=2)

        x_span = (x_upper_bound - x_lower_bound) / x_div_num
        y_span = (y_upper_bound - y_lower_bound) / y_div_num

        for xx in range(x_div_num):
            x = xx * x_span + int(x_lower_bound)
            z_sum[x] = {}
            for yy in range(y_div_num):
                y = yy * y_span + int(y_lower_bound)
                mask_x = (df[x_pal] > x) & (df[x_pal] <= x + x_span)
                mask_y = (df[y_pal] > y) & (df[y_pal] <= y + y_span)
                filtered_data = df[mask_x & mask_y]
                z_sum[x][y] = len(filtered_data)

        for x in z_sum:
            if x not in total_counts:
                total_counts[x] = {}
            for y in z_sum[x]:
                total_counts[x][y] = total_counts.get(x, {}).get(y, 0) + z_sum[x][y]

    x_values = []
    y_values = []
    z_values = []

    for x in total_counts:
        for y in total_counts[x]:
            x_values.append(x)
            y_values.append(y)
            z_values.append(total_counts[x][y])

    # 3Dグラフの作成
    for i in range(len(x_values)):
        fig.add_trace(go.Scatter3d(
            x=[x_values[i] + x_span / 100] * 5,
            y=[y_values[i]] * 5,
            z=[0, z_values[i], z_values[i], 0, 0],
            mode='lines',
            line=dict(width=10, color='rgba(0, 0, 0, 0.3)'),
            showlegend=False
        ), row=1, col=1)

        fig.add_trace(go.Scatter3d(
            x=[x_values[i]] * 5,
            y=[y_values[i]] * 5,
            z=[0, z_values[i], z_values[i], 0, 0],
            mode='lines',
            line=dict(width=10, color="blue"),
            showlegend=False
        ), row=1, col=1)

    return fig, total_counts

# ファイルのアップロード
col1, col2, col3 = st.columns([3, 3, 1])
with col1:
    uploaded_files = st.file_uploader("txtファイルをアップロードしてください(先)", type="txt", accept_multiple_files=True)
with col2:
    uploaded_files2 = st.file_uploader("別のtxtファイルをアップロードしてください", type="txt", accept_multiple_files=True)
with col3:
    sample_f = st.file_uploader("csvファイルをアップロードしてください", type=["csv"])

specific_string = "windarab"

# ファイルの読み込み

if uploaded_files is not None:
    dataframes, skiprows = process_files(uploaded_files, specific_string)

if uploaded_files2 is not None:
    dataframes2, skiprows = process_files(uploaded_files2, specific_string)

# グラフのパラメータ設定
if sample_f is not None:
    sample_df = pd.read_csv(sample_f, encoding='CP932')

    # skiprows1を使用してsample_columnsを設定
    sample_columns = 5 if skiprows == 2 else 2  # サンプルカラム数の確認
    sample_par = sample_df.iloc[1:, sample_columns].tolist()
    st.write(sample_par)
    sample_par = [x for x in sample_par if pd.notna(x)]  # リスト内包表記を使ってNaNを除外

    st.write(sample_par)

    with st.sidebar:
        x_pal = st.selectbox('x列を選択してください', sample_par)
        y_pal = st.selectbox('y列を選択してください', sample_par)
        x_lower_bound = st.number_input('xの下限値と', step=1)
        x_upper_bound = st.number_input('xの上限値を入力してください', value=100, step=10)
        y_lower_bound = st.number_input('yの下限値と', step=1)
        y_upper_bound = st.number_input('yの上限値を入力してください', value=200, step=10)
        x_div_num = st.number_input('x軸分割数', value=20)
        y_div_num = st.number_input('y軸分割数', value=20)

# グラフの作成
if dataframes:
    fig1, total_counts1 = create_fig(dataframes, x_pal, y_pal, x_lower_bound, x_upper_bound, y_lower_bound, y_upper_bound, x_div_num, y_div_num)
    st.plotly_chart(fig1, use_container_width=False)

if dataframes2:
    fig2, total_counts2 = create_fig(dataframes2, x_pal, y_pal, x_lower_bound, x_upper_bound, y_lower_bound, y_upper_bound, x_div_num, y_div_num)
    st.plotly_chart(fig2, use_container_width=False)