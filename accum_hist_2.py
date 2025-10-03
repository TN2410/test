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
data_files = st.file_uploader(
    "複数のデータファイルをアップロードしてください",
    type=["txt","csv"],
    accept_multiple_files=True
)

# パラメータCSVアップロード
param_csv_file = st.file_uploader(
    "パラメータCSVファイルをアップロードしてください",
    type=["csv"]
)

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
            # パラメータリストを取得（文字列化）
            param_list = param_df.iloc[1:, col_idx].dropna().astype(str).tolist()

            # メインパラメータAの選択（1つだけ選択）
            main_param = st.selectbox("ヒストグラムを作成するメインパラメータを1つ選択してください", param_list, index=0)

            # フィルタ用パラメータBの選択（「なし」も選べる）
            filter_param = st.selectbox("条件フィルタ用のパラメータを1つ選択してください（なし可）", ["なし"] + param_list, index=0)

            st.markdown("### 各パラメータの範囲を設定してください（積算対象の絞り込みに使用）")

            param_ranges = {}

            # メインパラメータAの範囲入力
            col1, col2 = st.columns(2)
            with col1:
                main_min = st.number_input(f"{main_param} の最小値", value=0.0, key=f"{main_param}_min", format="%.3f")
            with col2:
                main_max = st.number_input(f"{main_param} の最大値", value=1000.0, key=f"{main_param}_max", format="%.3f")
            param_ranges[main_param] = (main_min, main_max)

            # フィルタパラメータBの範囲入力（選択されていれば）
            if filter_param != "なし":
                col1, col2 = st.columns(2)
                with col1:
                    filter_min = st.number_input(f"{filter_param} の最小値", value=0.0, key=f"{filter_param}_min", format="%.3f")
                with col2:
                    filter_max = st.number_input(f"{filter_param} の最大値", value=1000.0, key=f"{filter_param}_max", format="%.3f")
                param_ranges[filter_param] = (filter_min, filter_max)

            all_data = pd.DataFrame(dtype=float)

            # 各ファイルからデータ読み込み・抽出
            for f in data_files:
                try:
                    df = pd.read_csv(f, sep="\t", encoding='utf-8', skiprows=skiprow, header=0, low_memory=False)

                    if file_type == "windarab":
                        df.columns = [text.split('[')[0].strip() for text in df.columns]

                    # 必要な列があるかチェック
                    required_columns = [main_param]
                    if filter_param != "なし":
                        required_columns.append(filter_param)

                    missing_params = [p for p in required_columns if p not in df.columns]
                    if missing_params:
                        st.warning(f"{f.name} にパラメータ {missing_params} の列がありません。")
                        continue

                    temp_df = pd.DataFrame()
                    for p in required_columns:
                        temp_df[p] = pd.to_numeric(df[p], errors='coerce')

                    # 範囲フィルタリング（すべてのパラメータが指定範囲内の行を抽出）
                    cond = pd.Series(True, index=temp_df.index)
                    for p in required_columns:
                        min_v, max_v = param_ranges[p]
                        cond &= (temp_df[p] >= min_v) & (temp_df[p] <= max_v)

                    temp_df = temp_df[cond].dropna()

                    if temp_df.empty:
                        st.warning(f"{f.name} に有効なデータがありません（範囲指定後）。")
                        continue

                    all_data = pd.concat([all_data, temp_df], ignore_index=True)

                except Exception as e:
                    st.warning(f"{f.name} の読み込みエラー: {e}")

            if all_data.empty:
                st.warning("有効なデータがありません。")
            else:
                bins_num = st.number_input("ビンの数（分割数）", min_value=10, max_value=50, value=20, step=5, key="hist_bins")

                if main_min >= main_max:
                    st.error("最小値は最大値より小さく設定してください。")
                else:
                    # 表示切替用のsession_state初期化
                    if "show_filtered" not in st.session_state:
                        st.session_state.show_filtered = False

                    # ボタンで切替
                    if st.button(f"表示切替（現在: {'Bの条件に一致するデータ' if st.session_state.show_filtered and filter_param != 'なし' else '全データ'}）"):
                        st.session_state.show_filtered = not st.session_state.show_filtered

                    # 表示用データ決定
                    if st.session_state.show_filtered and filter_param != "なし":
                        # Bの条件に一致するデータのAのヒストグラム
                        display_data = all_data[main_param].dropna()
                        # ただしmain_paramの範囲は常に適用済み
                        st.write(f"フィルタ条件に合致するデータ数: {len(display_data)}")
                    else:
                        # 全データのAのヒストグラム（Aの範囲フィルタは常に適用済み）
                        display_data = all_data[main_param].dropna()
                        st.write(f"全データ数: {len(display_data)}")

                    if len(display_data) == 0:
                        st.warning("表示対象のデータがありません。")
                    else:
                        bin_size = (main_max - main_min) / bins_num
                        fig = go.Figure(
                            data=[go.Histogram(
                                x=display_data,
                                xbins=dict(start=main_min, end=main_max, size=bin_size),
                                marker_color='navy',
                                opacity=0.6
                            )]
                        )
                        fig.update_layout(
                            title=f"{main_param} のヒストグラム - ビン数: {bins_num}",
                            xaxis_title=main_param,
                            yaxis_title="time(sec)",
                            bargap=0.1,
                            template="simple_white"
                        )
                        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("データファイル複数とパラメータCSVファイルをアップロードしてください。")