import streamlit as st
import pandas as pd
import numpy as np
import glob
import os
import matplotlib.pyplot as plt

st.title("WEC GT3 最高回転数抽出＆ヒストグラム表示")

# ユーザー入力：parameter名
parameter = st.text_input("抽出するパラメータ名を入力してください", value="SFTP")

# 選択肢
select = st.selectbox("データタイプを選択してください", options=["dpu", "windarab"], index=0)

if select == "windarab":
    dirname = r"C:\Users\1219829\OneDrive - トヨタ自動車株式会社\○開発資料\過給\177E\全ECUデータ変換"
    skiprows = 5
else:
    dirname = r"C:\Users\1219829\OneDrive - トヨタ自動車株式会社\○開発資料\WEC\全dpu変換"
    skiprows = 0

# ここは必要に応じて変更してください
dirname_2 = r"\DYNO_TEST\104E\P0062"
dirname_full = dirname + dirname_2
st.write("データフォルダ:", dirname_full)

if not os.path.exists(dirname_full):
    st.error("指定したフォルダが存在しません。パスを確認してください。")
else:
    maxmax = 0
    maxfile = ""
    df_all = pd.DataFrame()
    alldata = []

    # ファイル読み込み
    files = glob.glob(dirname_full + r"\**\*.txt", recursive=True)
    if len(files) == 0:
        st.warning("該当フォルダにtxtファイルが見つかりません。")
    else:
        progress_text = "ファイル読み込み中..."
        my_bar = st.progress(0)
        for i, f in enumerate(files):
            try:
                df = pd.read_csv(f, sep="\t", encoding='utf-8', skiprows=skiprows, low_memory=False)
                # 1行目を捨てる（元コードのdrop[0]に相当）
                if len(df) > 0:
                    df = df.drop(df.index[0])
                if parameter in df.columns:
                    maxrpm = df[parameter].astype(float).max()
                    if maxmax < maxrpm:
                        maxmax = maxrpm
                        maxfile = os.path.basename(f)
                    df_param = df[parameter].astype(float)
                    df_all = pd.concat([df_all, df_param], axis=0)
            except Exception as e:
                st.warning(f"{os.path.basename(f)} の読み込みでエラー: {e}")
            my_bar.progress(min((i+1)/len(files),1.0))
        my_bar.empty()

        if df_all.empty:
            st.warning("指定したパラメータのデータが見つかりません。")
        else:
            alldata = np.array(df_all)

            st.write(f"最大値: {maxmax} （ファイル: {maxfile}）")
            st.write(f"データ数: {len(alldata)}")

            # 追加設定：ユーザーが設定可能なヒストグラム範囲と分割数
            min_val = st.number_input("ヒストグラムの最小値", value=0.0, format="%.3f")
            max_val = st.number_input("ヒストグラムの最大値", value=10.0, format="%.3f")
            bins_num = st.number_input("ビンの数（分割数）", min_value=1, max_value=1000, value=10, step=1)

            if min_val >= max_val:
                st.error("最小値は最大値より小さく設定してください。")
            else:
                interval = (max_val - min_val) / bins_num
                bins = np.linspace(min_val, max_val, bins_num + 1)

                fig, ax = plt.subplots(figsize=(9,5))
                ax.hist(alldata, bins=bins, alpha=0.5, ec='navy')
                ax.set_xlim(min_val, max_val)
                ax.set_ylabel("time(sec)")
                ax.set_title(f"全{len(alldata)/3600:.4g}時間", fontname="Meiryo")

                st.pyplot(fig)

                # 画像保存の代わりにファイル名表示
                save_path = os.path.join(dirname_full, f"{parameter}_hyst_all.png")
                fig.savefig(save_path)
                st.write(f"グラフは以下に保存されました: {save_path}")