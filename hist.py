import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px  # 変更
import os

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

            fig = px.histogram(filtered_data, nbins=bins_num, range_x=[min_val, max_val],
                               labels={'value':'値', 'count':'度数'},
                               title=f"全{len(filtered_data)/3600:.4g}時間")

            st.plotly_chart(fig, use_container_width=True)

else:
    st.info("左上の「ファイルを選択」から複数ファイルをアップロードしてください。")