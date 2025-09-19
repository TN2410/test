import streamlit as st
import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt

st.title("ドラッグ＆ドロップしたファイルのパラメータ抽出＆ヒストグラム")

uploaded_files = st.file_uploader("ファイルを複数選択してください", accept_multiple_files=True, type=["txt", "csv"])

parameter = st.text_input("抽出するパラメータ名を入力してください", value="SFTP")

if uploaded_files and parameter:
    df_all = pd.DataFrame()
    maxmax = None
    maxfile = None

    for uploaded_file in uploaded_files:
        try:
        # 文字コードやsepは必要に応じて変更してください
            df = pd.read_csv(uploaded_file, sep="\t", encoding='utf-8', low_memory=False)
            if parameter in df.columns:
                # 文字列を数値に変換。変換不可はNaNに
                df_param = pd.to_numeric(df[parameter], errors='coerce')
                max_val = df_param.max()
                if maxmax is None or max_val > maxmax:
                    maxmax = max_val
                    maxfile = uploaded_file.name
                df_all = pd.concat([df_all, df_param], axis=0)
            else:
                st.warning(f"{uploaded_file.name} に列 {parameter} がありません。")
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
            filtered_data = alldata[(alldata >= min_val) & (alldata <= max_val)]

            # fig, ax = plt.subplots()
            # ax.hist(filtered_data, bins=bins_num, range=(min_val, max_val), color='navy', alpha=0.6)
            # ax.set_title(f"全{len(filtered_data)/3600:.4g}時間")
            # ax.set_xlabel(parameter)
            # ax.set_ylabel("time(sec)")
            # plt.grid(True)

            # st.pyplot(fig)

else:
    st.info("左上の「ファイルを選択」から複数ファイルをアップロードしてください。")
