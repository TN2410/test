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
                all_data = pd.Series(dtype=float)  # 累積用

                for f in data_files:
                    try:
                        # 1行目をヘッダーとして読み込む
                        df = pd.read_csv(f, sep="\t", encoding='utf-8', header=0, low_memory=False)
                        
                        if parameter not in df.columns:
                            st.warning(f"{f.name} にパラメータ '{parameter}' の列がありません。")
                            continue
                        
                        # 該当列の数値データを取得
                        col_data = pd.to_numeric(df[parameter], errors='coerce').dropna()
                        
                        if col_data.empty:
                            st.warning(f"{f.name} のパラメータ '{parameter}' に有効なデータがありません。")
                            continue

                        all_data = pd.concat([all_data, col_data], ignore_index=True)

                    except Exception as e:
                        st.warning(f"{f.name} の読み込みエラー: {e}")

                if all_data.empty:
                    st.warning("有効なデータがありません。")
                else:
                    st.write(all_data)
                    st.write(f"最大値: {all_data.max()}")
                    st.write(f"データ数: {len(all_data)}")

                    par_min_val = st.number_input("ヒストグラムの最小値", value=0.0, format="%.3f")
                    par_max_val = st.number_input("ヒストグラムの最大値", value=1000.0, format="%.3f")
                    bins_num = st.number_input("ビンの数（分割数）", min_value=10, max_value=20, value=10, step=1)

                    if par_min_val >= par_max_val:
                        st.error("最小値は最大値より小さく設定してください。")
                    else:
                        filtered_data = all_data[(all_data >= par_min_val) & (all_data <= par_max_val)]

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
                            title=f"全{len(filtered_data)/3600:.4g}時間",
                            xaxis_title=parameter,
                            yaxis_title="time(sec)",
                            bargap=0.1,
                            template="simple_white"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                       

else:
    st.info("データファイル複数とパラメータCSVファイルをアップロードしてください。")