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

#中間データファイルの保存先
INTERMEDIATE_DATA_FILE = 'intermediate_data.csv'

# 複数のCSVファイルを読み込む関数
def load_data(files):
    all_data = []
    for file in files:
        df = pd.read_csv(file)
        all_data.append(df)
    return pd.concat(all_data, ignore_index=True)

# 中間データファイルの生成
def create_intermediate_data(data):
    # 中間データをCSVファイルとして保存
    data.to_csv(INTERMEDIATE_DATA_FILE, index=False)

# 中間データファイルの読み込み
def load_intermediate_data():
    return pd.read_csv(INTERMEDIATE_DATA_FILE)

# 主な処理
def main():
    st.title('パラメータの累積時間棒グラフ')

    # ユーザーがCSVファイルをアップロードする
    uploaded_files = st.file_uploader("CSVファイルをアップロードしてください", type='csv', accept_multiple_files=True)

    # アップロードされたファイルがある場合の処理
    if uploaded_files:
        # 中間データファイルが存在する場合は読み込む
        if os.path.exists(INTERMEDIATE_DATA_FILE):
            data = load_intermediate_data()
        else:
            # アップロードされた全てのCSVファイルを読み込む
            data = load_data(uploaded_files)
            create_intermediate_data(data)

        # データの確認
        st.write("データのプレビュー:")
        st.dataframe(data)

        # ユーザーが累積したいパラメータをセレクトボックスで選択
        parameter = st.selectbox('累積したいパラメータを選択', data.columns)

        # アップロードしたファイルの中から累積したいファイルを選択するチェックボックス
        selected_files = []
        for i, file in enumerate(uploaded_files):
            if st.checkbox(f'ファイル: {file.name}', value=True):
                selected_files.append(file)

        # 選択されたファイルがある場合の処理
        if selected_files:
            # 選択されたファイルのデータを読み込む
            selected_data = load_data(selected_files)

            # ユーザーによる閾値の設定
            min_threshold = st.sidebar.slider('閾値の下限', 0, 100, 20)
            max_threshold = st.sidebar.slider('閾値の上限', 0, 100, 80)

            # 閾値に基づいてデータをフィルタリング
            filtered_data = selected_data[(selected_data[parameter] >= min_threshold) & (selected_data[parameter] <= max_threshold)]

            # 累積時間の計算
            filtered_data['timestamp'] = pd.to_datetime(filtered_data['timestamp'])  # タイムスタンプを日付型に変換
            filtered_data['cumulative_time'] = (filtered_data['timestamp'] - filtered_data['timestamp'].min()).dt.total_seconds()

            # グラフの描画
            plt.figure(figsize=(10, 6))
            plt.bar(filtered_data['timestamp'], filtered_data['cumulative_time'], width=0.01)
            plt.title('累積時間棒グラフ')
            plt.xlabel('時刻')
            plt.ylabel('累積時間（秒）')
            plt.xticks(rotation=45)
            st.pyplot(plt)
        else:
            st.warning("少なくとも1つのファイルを選択してください。")

if __name__ == '__main__':
    main()

###########################
# st.title("dpuデータ表示")

# # サンプルファイルアップロードし、選択パラメータリストを作成
# sample_f = st.file_uploader("csvファイルをアップロードしてください", type=["csv"])
# if sample_f is not None:
#     sample_df = pd.read_csv(sample_f,encoding="CP932")
#     sample_par = sample_df.iloc[:,5]#DPU用
#     mylist = [str(x) for x in sample_par]
#     newlist = [x for x in mylist if x != "nan"]
#     with st.sidebar:
#         #x_pal=st.selectbox('x列を選択してください', newlist)
#         y_pal=st.selectbox('積算パラメータを選択してください', newlist)
#         th_pal=st.selectbox('閾値パラメータを選択', newlist)
#         st.write(th_pal,"の")
#         lower_bound = st.number_input('の下限値と',step=1)
#         upper_bound = st.number_input('上限値を入力してください',value=100,step=1)
# #データファイルをアップロードし、グラフを作成する
# uploaded_files = st.file_uploader("txtファイルをアップロードしてください", type="txt",accept_multiple_files=True)
# if uploaded_files is not None:
#     dataframes = {}#この初期化した辞書型へ読み込んで全ロードデータを保存しておく
#     for uploaded_file in uploaded_files:
#         df = pd.read_csv(uploaded_file,sep="[\t\0]",engine='python')
#         df = df.iloc[1:]#dpuの場合は単位行があるために除外する 
#         # 時間データを秒に換算する 
#         time_format = "%H:%M:%S.%f"
#         df["Time"]= [datetime.strptime(time_str, time_format) for time_str in df["Time"]]
#         init_time = df["Time"][1]
#         df["Time"] = [(time - init_time).seconds for time in df["Time"]]
#         df = df.apply(pd.to_numeric)
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
