 #dpuデータを積算時間をstreamlitで表示する
#%matplotlib inline
import os,time,gc,math,glob
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
 
st.set_page_config(
    page_title="PLOT",  
    layout="wide", 
    initial_sidebar_state="auto")

# グローバル変数
data = None  # アップロードされたデータを格納する変数
selected_files_data = None  # 選択されたファイルのデータを格納する変数

def load_data(files):
    """複数のCSVファイルを読み込む関数"""
    all_data = []
    for file in files:
        df = pd.read_csv(file,sep="[\t\0]",engine='python')
        df = df.iloc[1:]#dpuの場合は単位行があるために除外する 
#         # 時間データを秒に換算する 
        time_format = "%H:%M:%S.%f"
        df["Time"] = pd.to_datetime(df["Time"], format=time_format)  # 直接datetimeに変換
        init_time = df["Time"].iloc[0]
        df["Time"] = (df["Time"] - init_time).dt.total_seconds()
        df = df.apply(pd.to_numeric, errors='coerce')
        all_data.append(df)

    return pd.concat(all_data, ignore_index=True)

def preprocess_data(selected_files):
    """選択されたファイルのデータを前処理する関数"""
    global selected_files_data
    selected_files_data = load_data(selected_files)

def plot_cumulative_time(parameter, min_threshold, max_threshold):
    """累積時間を計算してグラフを描画する関数"""
    # パラメータに基づいてデータをフィルタリング
    filtered_data = selected_files_data[
        (selected_files_data[parameter] >= min_threshold) &
        (selected_files_data[parameter] <= max_threshold)
    ]
    
    # タイムスタンプを日付型に変換
    filtered_data['timestamp'] = pd.to_datetime(filtered_data['timestamp'])
    
    # 累積時間の計算
    filtered_data['cumulative_time'] = (filtered_data['timestamp'] - filtered_data['timestamp'].min()).dt.total_seconds()

    # グラフの描画
    plt.figure(figsize=(10, 6))
    plt.bar(filtered_data['timestamp'], filtered_data['cumulative_time'], width=0.01)
    plt.title('累積時間棒グラフ')
    plt.xlabel('時刻')
    plt.ylabel('累積時間（秒）')
    plt.xticks(rotation=45)
    st.pyplot(plt)

def main():
    st.title('パラメータの累積時間棒グラフ')

    # サンプルファイルアップロードし、選択パラメータリストを作成
    sample_f = st.file_uploader("csvファイルをアップロードしてください", type=["csv"])
    if sample_f is not None:
        sample_df = pd.read_csv(sample_f,encoding="CP932")
        sample_par = sample_df.iloc[:,5]#DPU用
        mylist = [str(x) for x in sample_par]
        newlist = [x for x in mylist if x != "nan"]

    # ユーザーがCSVファイルをアップロードする
    uploaded_files = st.file_uploader("CSVファイルをアップロードしてください", type='txt', accept_multiple_files=True)

    # アップロードされたファイルがある場合の処理
    if uploaded_files:
        # アップロードされたデータを読み込む
        global data
        data = load_data(uploaded_files)

        # データのプレビュー
        st.write("データのプレビュー:")
        st.dataframe(data)
        with st.sidebar:
            parameter =st.selectbox('積算パラメータを選択してください', newlist)
            th_pal=st.selectbox('閾値パラメータを選択', newlist)
            st.write(th_pal,"の")
            min_threshold = st.number_input('の下限値と',step=1)
            max_threshold = st.number_input('上限値を入力してください',value=100,step=1)

        # アップロードしたファイルの中から累積したいファイルを選択するチェックボックス
        selected_files = []
        for i, file in enumerate(uploaded_files):
            if st.checkbox(f'ファイル: {file.name}', value=True):
                selected_files.append(file)

        # 選択されたファイルがある場合の処理
        if selected_files:
            st.write(selected_files)
            # 選択されたファイルのデータを前処理
            preprocess_data(selected_files)
            # ユーザーによる閾値の設定


            # グラフの描画
            plot_cumulative_time(parameter, min_threshold, max_threshold)
        else:
            st.warning("少なくとも1つのファイルを選択してください。")

if __name__ == '__main__':
    main()

# #データファイルをアップロードし、グラフを作成する
#     dataframes = {}#この初期化した辞書型へ読み込んで全ロードデータを保存して
#         max_value = int(df[th_pal].max())
#         min_value = int(df[th_pal].min())

#         query_string = f"{th_pal} >= @lower_bound & {th_pal} <= @upper_bound"    
#         filtered_data = df.query(query_string)
#         dataframes[uploaded_file.name] = filtered_data

#     #　散布図のプロット
#     sum_y = 0
#     if dataframes:
#         fig=plt.figure(figsize=(16, 9))
#         # 各データフレームの表示を制御するボタンを作成
#         for filename, filtered_data in dataframes.items():
#             # ボタンを作成（ファイル名をボタン名として使用）
#             with st.sidebar:
#                 show_data = st.checkbox("{} を表示".format(filename), value=True)
#             # ボタンが選択されている場合に散布図をプロット
#             if show_data:
#                 # x列とy列を指定（ここでは仮に 　'x' と 'y' 列を使用）
#                 selected_ydata = filtered_data[y_pal]
#                 y=selected_ydata.astype(float)
#                 plt.bar(filename,len(y))
#                 sum_y += len(y)
#                 #plt.title(file.name)
                
#         plt.legend(bbox_to_anchor=(1.05, 1.0), loc="upper left")
#         plt.title("{}_sum = {:.2f} Hr".format(filename,sum_y/3600),font="Meiryo",fontsize=20)
#         #plt.ylabel(y_pal)
#         st.pyplot(fig)
