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
        skiprows = 5 if initial_lines.apply(lambda x: x.astype(str).str.contains(specific_string).any(), axis=1).any() else 0
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
    )

    all_z_values = []  # すべてのz値を保存するリスト

    for filename, df in dataframes.items():
        if df.empty:
            st.warning(f"{filename} は空のファイルです。")
            continue

        # カラム名の存在確認
        if x_pal not in df.columns or y_pal not in df.columns:
            st.warning(f"{filename} にはカラム '{x_pal}' または '{y_pal}' が存在しません。")
            continue
            
        if "Time" in df.columns:
            df = df.iloc[1:]  # DPUの場合は単位行を除外
            time_format = "%H:%M:%S.%f"
            df["Time"] = [datetime.strptime(time_str, time_format) for time_str in df["Time"]]
            init_time = df["Time"].iloc[0]
            df["Time"] = [(time - init_time).seconds for time in df["Time"]]
            df = df.apply(pd.to_numeric, errors='coerce')

        # z_sumの計算
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
                all_z_values.append(z_sum[x][y])  # z値をリストに追加

        # スキャッタープロットの追加
        fig.add_trace(go.Scatter(x=df[x_pal], y=df[y_pal], mode='markers', name=filename), row=1, col=2)

    # z値の正規化
    if all_z_values:  # z値が存在する場合
        min_z = min(all_z_values)
        max_z = max(all_z_values)
        #if (max_z - min_z) !=0:
        #    normalized_z_values = [(z - min_z) / (max_z - min_z) for z in all_z_values]
        #else :
        normalized_z_values = all_z_values
        # 正規化したz値を使用して3Dグラフを作成
    #else :
    #    normalized_z_values = []
        st.write(x_values)

        for i in range(len(normalized_z_values)):
            fig.add_trace(go.Scatter3d(
                x=[x_values[i] + x_span / 100] * 5,
                y=[y_values[i]] * 5,
                z=[0, normalized_z_values[i], normalized_z_values[i], 0, 0],
                mode='lines',
                line=dict(width=10, color='rgba(0, 0, 0, 0.3)'),
                showlegend=False
            ), row=1, col=1)

            fig.add_trace(go.Scatter3d(
                x=[x_values[i]] * 5,
                y=[y_values[i]] * 5,
                z=[0, normalized_z_values[i], normalized_z_values[i], 0, 0],
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
    # skiprowsを使用してsample_columnsを設定
    sample_columns = 5 if skiprows == 0 else 2  # サンプルカラム数の確認
    sample_par = sample_df.iloc[1:, sample_columns].tolist()
    sample_par = list(filter(pd.notna, sample_par))
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
    st.plotly_chart(fig1)

if dataframes2:
    fig2, total_counts2 = create_fig(dataframes2, x_pal, y_pal, x_lower_bound, x_upper_bound, y_lower_bound, y_upper_bound, x_div_num, y_div_num)
    st.plotly_chart(fig2)

# 有意差の検出
if len(total_counts1) > 0 and len(total_counts2) > 0:
    # 2つの正規化されたzデータの有意差を検出
    t_statistic, p_value = stats.ttest_ind(normalized_z_values1, normalized_z_values2)
    st.write(f"t統計量: {t_statistic}, p値: {p_value}")