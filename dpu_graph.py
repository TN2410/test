# 必要なライブラリのインポート
import os
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats

# Streamlitの設定
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

def create_fig(dataframes, x_pal, y_pal, x_lower_bound, x_upper_bound, y_lower_bound, y_upper_bound, x_div_num, y_div_num, skiprows):
    total_counts = {}
    z_values_dict = {}  # 各ペアのz値を保存する辞書
    all_z_values = []  # すべてのz値を保存するリスト
    x_values = []  # xの値を保存するリスト
    y_values = []  # yの値を保存するリスト

    fig = make_subplots(
        rows=1,
        cols=2,
        specs=[[{"type": "surface"}, {"type": "scatter"}]],
        subplot_titles=("時間頻度", "Scatter Plot"),
    )

    for filename, df in dataframes.items():
        if df.empty:
            st.warning(f"{filename} は空のファイルです。")
            continue

        # カラム名の存在確認
        if skiprows == 5:
            df.columns = [text.split('[')[0].strip() for text in df.columns]
        
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
            for yy in range(y_div_num):
                y = yy * y_span + int(y_lower_bound)
                mask_x = (df[x_pal] > x) & (df[x_pal] <= x + x_span)
                mask_y = (df[y_pal] > y) & (df[y_pal] <= y + y_span)
                filtered_data = df[mask_x & mask_y]
                z_value = len(filtered_data)
                
                # z値を辞書に保存
                if z_value > 0:
                    z_values_dict[(x, y)] = z_value
                    all_z_values.append(z_value)
                    x_values.append(x)
                    y_values.append(y)

        # スキャッタープロットの追加
        fig.add_trace(go.Scatter(x=df[x_pal], y=df[y_pal], mode='markers', name=filename), row=1, col=2)

    # タイトルを更新
    total_z_value = sum(all_z_values)
    fig.layout.annotations[0].text = f"時間頻度 (Total: {total_z_value/3600:.2f}Hrs)"

    # z値の正規化
    normalized_z_values = []
    
    if all_z_values:  # z値が存在する場合
        min_z = min(all_z_values)
        max_z = max(all_z_values)
        if total_z_value > 0 :
            normalized_z_values = [ z / total_z_value for z in all_z_values]
        else:
            normalized_z_values = all_z_values

        # 正規化したz値を使用して3Dグラフを
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

    # y軸の上下限を設定
    fig.update_xaxes(range=[x_lower_bound, x_upper_bound], row=1, col=2)
    fig.update_yaxes(range=[y_lower_bound, y_upper_bound], row=1, col=2)

    fig.update_layout(
        height = 600,
        width = 1400,
        scene=dict(
            xaxis=dict(range=[x_lower_bound, x_upper_bound]),
            yaxis=dict(range=[y_lower_bound, y_upper_bound]),
            camera=dict(
                eye=dict(x=1, y=-1, z=1)
            ),
            xaxis_title=x_pal,
            yaxis_title=y_pal,
            zaxis_title='頻度'
        ),
        xaxis_title=x_pal,
        yaxis_title=y_pal
    )
    return fig, z_values_dict, normalized_z_values, total_z_value

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
dataframes, skiprows = None, 0
if uploaded_files:
    with st.spinner("ファイル処理中..."):
        dataframes, skiprows = process_files(uploaded_files, specific_string)
if uploaded_files2:
    with st.spinner("ファイル処理中..."):
        dataframes2, skiprows = process_files(uploaded_files2, specific_string)

# グラフのパラメータ設定
if sample_f is not None:
    sample_df = pd.read_csv(sample_f, encoding='CP932')
    sample_columns = 5 if skiprows == 0 else 2
    sample_par = sample_df.iloc[:, sample_columns].tolist()
    sample_par = list(filter(pd.notna, sample_par))
    
    if skiprows == 0:
        initial_x_pal, initial_y_pal = "NE", "P_Manifold1"
        initial_x_lower_bound, initial_x_upper_bound = 0, 10000 
        initial_y_lower_bound, initial_y_upper_bound = 0, 250
    else:
        initial_x_pal, initial_y_pal = "nmot", "pboost"
        initial_x_lower_bound, initial_x_upper_bound = 0, 8000 
        initial_y_lower_bound, initial_y_upper_bound = 0, 2000

    with st.sidebar:
        x_pal = st.selectbox('x列を選択してください', sample_par, index=sample_par.index(initial_x_pal))
        y_pal = st.selectbox('y列を選択してください', sample_par, index=sample_par.index(initial_y_pal))
        x_lower_bound = st.number_input('xの下限値を入力してください', value=initial_x_lower_bound, step=1)
        x_upper_bound = st.number_input('xの上限値を入力してください', value=initial_x_upper_bound, step=10)
        y_lower_bound = st.number_input('yの下限値を入力してください', value=initial_y_lower_bound, step=1)
        y_upper_bound = st.number_input('yの上限値を入力してください', value=initial_y_upper_bound, step=10)
        x_div_num = st.number_input('x軸分割数', value=20)
        y_div_num = st.number_input('y軸分割数', value=20)

# グラフの作成
if dataframes:
    with st.spinner("グラフを作成中..."):
        fig1, z_values1, normalized_z_values1, total_z_value1 = create_fig(dataframes, x_pal, y_pal, x_lower_bound, x_upper_bound, y_lower_bound, y_upper_bound, x_div_num, y_div_num, skiprows)
        st.plotly_chart(fig1)

    # CSV出力ボタン
    if st.button("のデータをCSV出力"):
        output_data1 = {
            'x': x_values,  # xの値を出力
            'y': y_values,  # yの値を出力
            'z': z_values1,  # 元のz値を出力
            'normalized_z': normalized_z_values1  # 無次元化されたz値を出力
        }
        output_df1 = pd.DataFrame(output_data1)
        output_csv1 = output_df1.to_csv(index=False)
        st.download_button(
            label=f"{uploaded_files[0].name}のCSVをダウンロード",
            data=output_csv1,
            file_name=f"{uploaded_files[0].name}.csv",
            mime='text/csv'
        )

if dataframes2:
    with st.spinner("別のグラフを作成中..."):
        fig2, z_values2, normalized_z_values2, total_z_value2 = create_fig(dataframes2, x_pal, y_pal, x_lower_bound, x_upper_bound, y_lower_bound, y_upper_bound, x_div_num, y_div_num, skiprows)
        st.plotly_chart(fig2)

    # CSV出力ボタン
    if st.button("データをCSV出力"):
        output_data2 = {
            'x': x_values,  # xの値を出力
            'y': y_values,  # yの値を出力
            'z': z_values2,  # 元のz値を出力
            'normalized_z': normalized_z_values2  # 無次元化されたz値を出力
        }
        output_df2 = pd.DataFrame(output_data2)
        output_csv2 = output_df2.to_csv(index=False)
        st.download_button(
            label=f"{uploaded_files2[0].name}のCSVをダウンロード",
            data=output_csv2,
            file_name=f"{uploaded_files2[0].name}.csv",
            mime='text/csv'
        )

# 有意差の検出
if normalized_z_values1 and normalized_z_values2:  # 無次元化されたz値を使用
    # 各無次元化z値のリストを作成
    z_values_1 = normalized_z_values1  # 1つ目の無次元化z値
    z_values_2 = normalized_z_values2  # 2つ目の無次元化z値

    # t検定
    t_statistic, p_value_t = stats.ttest_ind(z_values_1, z_values_2)
    st.write(f"t統計量: {t_statistic:.3f}, p値: {p_value_t:.3g}")
    if p_value_t < 0.05:
        st.write("有意差あり")

    # Mann-Whitney U検定
    u_statistic, p_value_u = stats.mannwhitneyu(z_values_1, z_values_2, alternative='two-sided')
    st.write(f"U統計量: {u_statistic:.3f}, p値: {p_value_u:.3g}")
    if p_value_u < 0.05:
        st.write("有意差あり")
