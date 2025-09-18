import sys
print(sys.executable)
print(sys.path)
import plotly
print(plotly.__file__)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.title("ドラッグ＆ドロップしたファイルのパラメータ抽出＆ヒストグラム")

uploaded_files = st.file_uploader("ファイルを複数選択してください", accept_multiple_files=True, type=["txt", "csv"])

parameter = st.text_input("抽出するパラメータ名を入力してください", value="SFTP")

if uploaded_files and parameter:
    df_all = pd.DataFrame()
    maxmax = None
    maxfile = None

    for uploaded_file in uploaded_files:
        try:
            df = pd.read_csv(uploaded_file, sep="\t", encoding='utf-8', low_memory=False)
            if parameter in df.columns:
                max_val = df[parameter].astype(float).max()
                if maxmax is None or max_val > maxmax:
                    maxmax = max_val
                    maxfile = uploaded_file.name
                df_param = df[parameter].astype(float)
                df_all = pd.concat([df_all, df_param], axis=0)
        except Exception as e:
            st.warning(f"{uploaded_file.name} の読み込みでエラー: {e}")

    if df_all.empty:
        st.warning("指定したパラメータのデータが見つかりません。")
    else:
        alldata = np.array(df_all)
        st.write(f"最大値: {maxmax} （ファイル: {maxfile}）")
        st.write(f"データ数: {len(alldata)}")

        min_val = st.number_input("ヒストグラムの最小値", value=0.0, format="%.3f")
        max_val = st.number_input("ヒストグラムの最大値", value=10.0, format="%.3f")
        bins_num = st.number_input("ビンの数（分割数）", min_value=1, max_value=1000, value=10, step=1)

        if min_val >= max_val:
            st.error("最小値は最大値より小さく設定してください。")
        else:
            # 範囲内のデータに絞る
            filtered_data = alldata[(alldata >= min_val) & (alldata <= max_val)]

            # ビン境界を計算
            bins = np.linspace(min_val, max_val, bins_num + 1)
            counts, bin_edges = np.histogram(filtered_data, bins=bins)

            fig = make_subplots(rows=1, cols=1)

            fig.add_trace(
                go.Bar(
                    x=bin_edges[:-1],
                    y=counts,
                    width=(bin_edges[1] - bin_edges[0]),
                    marker_color='navy',
                    opacity=0.6,
                    name='度数'
                ),
                row=1, col=1
            )

            fig.update_layout(
                title=f"全{len(filtered_data)/3600:.4g}時間",
                xaxis_title=parameter,
                yaxis_title="time(sec)",
                bargap=0.1,
                template="plotly_white",
                font=dict(family="Meiryo", size=14)
            )

            st.plotly_chart(fig, use_container_width=True)

else:
    st.info("左上の「ファイルを選択」から複数ファイルをアップロードしてください。")
