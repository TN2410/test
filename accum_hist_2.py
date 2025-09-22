import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.title("自動判定によるパラメータ抽出＆ヒストグラム")

uploaded_files = st.file_uploader("テキストファイルを複数選択してください", accept_multiple_files=True, type=["txt", "csv"])

param_csv = st.file_uploader("パラメータ一覧CSVファイルを選択してください", type=["csv"])

def detect_file_type(file) -> str:
    """
    ファイル先頭数行を読んで 'windarab' または 'dpu' を判定
    """
    try:
        head = file.read(2048).decode('utf-8', errors='ignore').lower()
        file.seek(0)  # 読み込み位置を戻す
        if "windarab" in head:
            return "windarab"
        elif "dpu" in head:
            return "dpu"
        else:
            return "unknown"
    except Exception as e:
        return "unknown"

if uploaded_files and param_csv:
    # パラメータCSV読み込み
    try:
        param_df = pd.read_csv(param_csv)
        # パラメータ名のカラム名が分からなければ適宜変更してください
        if 'parameter' in param_df.columns:
            param_options = param_df['parameter'].dropna().unique().tolist()
        else:
            param_options = param_df.columns.tolist()
    except Exception as e:
        st.error(f"パラメータCSVの読み込みエラー: {e}")
        param_options = []

    if not param_options:
        st.warning("パラメータCSVから選択肢が取得できません。")
    else:
        parameter = st.selectbox("抽出するパラメータを選択してください", param_options)

        df_all = pd.Series(dtype=float)
        max_val_overall = None
        max_file_overall = None

        for uploaded_file in uploaded_files:
            file_type = detect_file_type(uploaded_file)

            if file_type == "windarab":
                col_index = 1  # 2列目
            elif file_type == "dpu":
                col_index = 4  # 5列目
            else:
                st.warning(f"{uploaded_file.name} のファイルタイプが判定できません。スキップします。")
                continue

            try:
                # ファイルをPandasで読み込み（区切り文字は適宜調整してください）
                df = pd.read_csv(uploaded_file, sep="\t", encoding='utf-8', header=None, low_memory=False)
                # 列数チェック
                if col_index >= len(df.columns):
                    st.warning(f"{uploaded_file.name} は期待した列数がありません。")
                    continue

                # パラメータ列の名前を取得して、パラメータCSVの選択肢とマッチングしてフィルターする場合はここで処理可能
                data_col = df.iloc[:, col_index]

                # 数値化してNaNを除去
                data_num = pd.to_numeric(data_col, errors='coerce').dropna()

                if data_num.empty:
                    st.warning(f"{uploaded_file.name} の指定列に有効なデータがありません。")
                    continue

                max_val = data_num.max()
                if max_val_overall is None or max_val > max_val_overall:
                    max_val_overall = max_val
                    max_file_overall = uploaded_file.name

                df_all = pd.concat([df_all, data_num], ignore_index=True)

            except Exception as e:
                st.warning(f"{uploaded_file.name} の読み込みエラー: {e}")

        if df_all.empty:
            st.warning("有効なデータがありません。")
        else:
            st.write(f"最大値: {max_val_overall} （ファイル: {max_file_overall}）")
            st.write(f"データ数: {len(df_all)}")

            min_val = st.number_input("ヒストグラムの最小値", value=0.0, format="%.3f")
            max_val = st.number_input("ヒストグラムの最大値", value=10.0, format="%.3f")
            bins_num = st.number_input("ビンの数（分割数）", min_value=1, max_value=1000, value=10, step=1)

            if min_val >= max_val:
                st.error("最小値は最大値より小さく設定してください。")
            else:
                filtered_data = df_all[(df_all >= min_val) & (df_all <= max_val)]

                fig = go.Figure(
                    data=[go.Histogram(
                        x=filtered_data,
                        nbinsx=bins_num,
                        xbins=dict(start=min_val, end=max_val),
                        marker_color='navy',
                        opacity=0.6
                    )]
                )
                fig.update_layout(
                    title=f"全{len(filtered_data)/3600:.4g}時間",
                    xaxis_title=parameter,
                    yaxis_title="time(sec)",
                    bargap=0.1,
                    template="simple_white"
                )
                st.plotly_chart(fig, use_container_width=True)
else:
    st.info("テキストファイル複数とパラメータCSVファイルをアップロードしてください。")