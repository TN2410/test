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

st.title("複数データファイルの自動判定＆累積パラメータ抽出")

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
        # すべてのアップロードファイルについて判定し、判定結果を収集
        file_types = []
        for f in data_files:
            ft = detect_file_type(f)
            file_types.append(ft)

        # 判定結果が異なる場合は最初のファイルのタイプを使う（警告表示）
        if len(set(file_types)) > 1:
            st.warning("アップロードされたファイルで判定結果が異なります。処理は最初のファイルの判定を使用します。")
        file_type = file_types[0]

        if file_type == 'windarab':
            col_idx = 2  # 2列目（0始まりのインデックス）
        elif file_type == 'dpu':
            col_idx = 5  # 5列目
        else:
            st.error("ファイルタイプ判定できません。")
            col_idx = None

        if col_idx is not None:
            # パラメータリストを該当列の2行目以降から取得（1行目はインデックス0）
            param_list = param_df.iloc[1:, col_idx].dropna().astype(str).tolist()
            parameter = st.selectbox("抽出するパラメータを選択してください", param_list)

            if parameter:
                # 全ファイルの該当列データを累積
                all_data = pd.Series(dtype=float)  # ループ外で初期化
                max_val_overall = None
                max_file_overall = None

                for f in data_files:
                    try:
                        df = pd.read_csv(f, sep="\t", encoding='utf-8', header=None, low_memory=False)
                        if col_idx >= len(df.columns):
                            st.warning(f"{f.name} は期待した列数がありません。")
                            continue
                        col_data = df.iloc[:, col_idx]
                        numeric_data = pd.to_numeric(col_data, errors='coerce').dropna()
                        if numeric_data.empty:
                            st.warning(f"{f.name} の指定列に有効なデータがありません。")
                            continue
                        max_val = numeric_data.max()
                        if max_val_overall is None or max_val > max_val_overall:
                            max_val_overall = max_val
                            max_file_overall = f.name
                        # ここで累積
                        all_data = pd.concat([all_data, numeric_data], ignore_index=True)
                        st.write(len(all_data))
                    except Exception as e:
                        st.warning(f"{f.name} の読み込みエラー: {e}")

                if all_data.empty:
                    st.warning("有効なデータがありません。")
                else:
                    st.write(f"最大値: {max_val_overall} （ファイル: {max_file_overall}）")
                    st.write(f"データ数: {len(all_data)}")

                    min_val = st.number_input("ヒストグラムの最小値", value=0.0, format="%.3f")
                    max_val = st.number_input("ヒストグラムの最大値", value=10.0, format="%.3f")
                    bins_num = st.number_input("ビンの数（分割数）", min_value=1, max_value=1000, value=10, step=1)

                    if min_val >= max_val:
                        st.error("最小値は最大値より小さく設定してください。")
                    else:
                        filtered_data = all_data[(all_data >= min_val) & (all_data <= max_val)]

                        bin_size = (max_val - min_val) / bins_num

                        fig = go.Figure(
                            data=[go.Histogram(
                                x=filtered_data,
                                xbins=dict(start=min_val, end=max_val, size=bin_size),
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
    st.info("データファイル複数とパラメータCSVファイルをアップロードしてください。")