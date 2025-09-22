import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.title("累積パラメータ選択とヒストグラム表示")

# パラメータCSVアップロード
param_csv_file = st.file_uploader("パラメータCSVファイルをアップロードしてください", type=["csv"])

if param_csv_file:
    try:
        param_df = pd.read_csv(param_csv_file)
    except Exception as e:
        st.error(f"パラメータCSVの読み込みエラー: {e}")
        param_df = None
else:
    param_df = None

if param_df is not None:
    # CSVの列名リストを取得
    columns = param_df.columns.tolist()
    # 累積パラメータを選択
    cumulative_param = st.selectbox("累積パラメータを選択してください", columns)

    # 選択したパラメータのデータを取得
    data = pd.to_numeric(param_df[cumulative_param], errors='coerce').dropna()

    st.write(f"選択された累積パラメータ: {cumulative_param}")
    st.write(f"データ数: {len(data)}")

    # ヒストグラムのパラメータ入力
    min_val = st.number_input("ヒストグラムの最小値", value=float(data.min()), format="%.3f")
    max_val = st.number_input("ヒストグラムの最大値", value=float(data.max()), format="%.3f")
    bins_num = st.number_input("ビンの数", min_value=1, max_value=1000, value=10, step=1)

    if min_val >= max_val:
        st.error("最小値は最大値より小さく設定してください。")
    else:
        filtered_data = data[(data >= min_val) & (data <= max_val)]

        fig = go.Figure(
            data=[go.Histogram(
                x=filtered_data,
                nbinsx=bins_num,
                xbins=dict(start=min_val, end=max_val),
                marker_color='navy',
                opacity=0.6
            )])