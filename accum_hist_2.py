import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

def detect_file_type(file) -> str:
    """ファイル内容に 'windarab' があれば 'windarab'、なければ 'dpu' と判定"""
    try:
        content = file.read(4096).decode('utf-8', errors='ignore').lower()
        file.seek(0)  # 読み込み位置を戻す
        if 'windarab' in content:
            return 'windarab'
        else:
            return 'dpu'
    except Exception as e:
        return 'unknown'

st.title("データ用ファイル内容で判定しパラメータ選択")

# データ用ファイル（判定対象）アップロード
data_file = st.file_uploader("データ用ファイルをアップロードしてください", type=["txt", "csv"])

# パラメータCSVアップロード
param_csv_file = st.file_uploader("パラメータCSVファイルをアップロードしてください", type=["csv"])

if data_file and param_csv_file:
    file_type = detect_file_type(data_file)

    try:
        param_df = pd.read_csv(param_csv_file, header=None)
    except Exception as e:
        st.error(f"パラメータCSVの読み込みエラー: {e}")
        param_df = None

    if param_df is not None:
        if file_type == 'windarab':
            col_idx = 1  # 2列目（0始まり）
        elif file_type == 'dpu':
            col_idx = 4  # 5列目
        else:
            st.error("ファイルタイプ判定できません。")
            col_idx = None

        if col_idx is not None:
            # 2行目以降のパラメータ文字列を取得
            param_list = param_df.iloc[1:, col_idx].dropna().astype(str).tolist()
            parameter = st.selectbox("抽出するパラメータを選択してください", param_list)

            # ここ以降は選択したパラメータを使った処理を記述
            st.write(f"判定ファイルタイプ: {file_type}")
            st.write(f"選択パラメータ: {parameter}")

            # 例：累積データCSVアップロード・ヒストグラム表示などを続ける

else:
    st.info("データ用ファイルとパラメータCSVファイルの両方をアップロードしてください。")