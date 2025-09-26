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

st.title("各種パラメータヒストグラム")

# 複数のデータ用ファイルアップロード
data_files = st.file_uploader("複数のデータファイルをアップロードしてください", type=["txt","csv"], accept_multiple_files=True)

# パラメータCSVアップロード
param_csv_file = st.file_uploader("パラメータCSVファイルをアップロードしてください", type=["csv"])

if data_files and param_csv_file:
    try:
        param_df = pd.read_csv(param_csv_file, header=None, encoding="CP932")
    except Exception as e:
        st.error(f"パラメータCSVの読み込みエラー: {e}")
        param_df = None

    if param_df is not None:
        # アップロードファイルの判定結果収集
        file_types = [detect_file_type(f) for f in data_files]

        if len(set(file_types)) > 1:
            st.warning("アップロードされたファイルで判定結果が異なります。処理は最初のファイルの判定を使用します。")
        file_type = file_types[0]

        if file_type == 'windarab':
            col_idx = 2
            skiprow = 5
        elif file_type == 'dpu':
            col_idx = 5
            skiprow = 0
        else:
            st.error("ファイルタイプ判定できません。")
            col_idx = None

        if col_idx is not None:
            param_list = param_df.iloc[1:, col_idx].dropna().astype(str).tolist()
            parameters = st.multiselect("抽出するパラメータを選択してください（複数選択可）", param_list)

            if parameters:
                all_data = pd.DataFrame(dtype=float)  # 複数パラメータのデータ格納用

                for f in data_files:
                    try:
                        df = pd.read_csv(f, sep="\t", encoding='utf-8', skiprows=skiprow, header=0, low_memory=False)

                        if file_type == "windarab":
                            df.columns = [text.split('[')[0].strip() for text in df.columns]

                        missing_params = [p for p in parameters if p not in df.columns]
                        if missing_params:
                            st.warning(f"{f.name} にパラメータ {missing_params} の列がありません。")
                            continue

                        temp_df = pd.DataFrame()
                        for p in parameters:
                            temp_df[p] = pd.to_numeric(df[p], errors='coerce')
                        temp_df = temp_df.dropna()

                        if temp_df.empty:
                            st.warning(f"{f.name} に有効なデータがありません。")
                            continue

                        all_data = pd.concat([all_data, temp_df], ignore_index=True)

                    except Exception as e:
                        st.warning(f"{f.name} の読み込みエラー: {e}")

                if all_data.empty:
                    st.warning("有効なデータがありません。")
                else:
                    par_min_val = st.number_input("ヒストグラムの最小値", value=0.0, format="%.3f")
                    par_max_val = st.number_input("ヒストグラムの最大値", value=1000.0, format="%.3f")
                    bins_num = st.number_input("ビンの数（分割数）", min_value=10, max_value=50, value=20, step=5)
                    bins_num = int(bins_num)

                    if par_min_val >= par_max_val:
                        st.error("最小値は最大値より小さく設定してください。")
                    else:
                        if len(parameters) == 1:
                            # 単一パラメータのヒストグラム
                            param = parameters[0]
                            filtered_data = all_data[param][(all_data[param] >= par_min_val) & (all_data[param] <= par_max_val)]

                            st.write(f"最大値: {filtered_data.max()}")
                            st.write(f"データ数: {len(filtered_data)}")

                            bin_size = (par_max_val - par_min_val) / bins_num

                            fig = go.Figure(
                                data=[go.Histogram(
                                    x=filtered_data,
                                    xbins=dict(start=par_min_val, end=par_max_val, size=bin_size),
                                    marker_color='navy',
                                    opacity=0.6
                                )]
                            )

                            fig.update_layout(
                                title=f"{param} のヒストグラム - 全{len(filtered_data)/3600:.4g}時間 - ビン数: {bins_num}",
                                xaxis_title=param,
                                yaxis_title="time(sec)",
                                bargap=0.1,
                                template="simple_white"
                            )
                            st.plotly_chart(fig, use_container_width=True)

                        else:
                            # 複数パラメータの積のヒストグラム
                            product_series = all_data.prod(axis=1)
                            filtered_data = product_series[(product_series >= par_min_val) & (product_series <= par_max_val)]

                            st.write(f"最大値: {filtered_data.max()}")
                            st.write(f"データ数: {len(filtered_data)}")

                            bin_size = (par_max_val - par_min_val) / bins_num

                            fig = go.Figure(
                                data=[go.Histogram(
                                    x=filtered_data,
                                    xbins=dict(start=par_min_val, end=par_max_val, size=bin_size),
                                    marker_color='navy',
                                    opacity=0.6
                                )]
                            )

                            fig.update_layout(
                                title=f"パラメータ積 ({' × '.join(parameters)}) のヒストグラム - 全{len(filtered_data)/3600:.4g}時間 - ビン数: {bins_num}",
                                xaxis_title="積の値",
                                yaxis_title="time(sec)",
                                bargap=0.1,
                                template="simple_white"
                            )
                            st.plotly_chart(fig, use_container_width=True)

else:
    st.info("データファイル複数とパラメータCSVファイルをアップロードしてください。")