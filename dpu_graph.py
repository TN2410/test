 
#dpuデータをstreamlitで表示する
#%matplotlib inline
import os,time,gc,math,glob
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import re
from mpl_toolkits.mplot3d import Axes3D

# windarab と　dpu　ファイルの差を自動検知して、サンプルを変更する
st.set_page_config(
    page_title="PLOT",  
    layout="wide", 
    initial_sidebar_state="auto")
st.title("windarab or dpu データ表示")

@st.cache_data
def load_uploaded_file(uploaded_file, skiprows):
    return pd.read_csv(uploaded_file, sep="[\t\0]", skiprows=skiprows, engine="python")

uploaded_files = st.file_uploader("txtファイルをアップロードしてください(先)", type="txt",accept_multiple_files=True 
                                 )
specific_string = "windarab"  # ここに検索したい文字を設定
if uploaded_files is not None:
    sample_columns, skiprows = None, None
    dataframes = {}
    for uploaded_file in uploaded_files:
       #ファイルを簡易的に読み込んでwindarabデータを　5行削除する
        initial_lines = pd.read_csv(uploaded_file, nrows=2)
     # ファイルを再度読み込むために、元のファイルポインタを最初に戻す
        uploaded_file.seek(0)
        if initial_lines.apply(lambda x: x.astype(str).str.contains(specific_string).any(), axis=1).any():
            sample_columns = 2
            skiprows = 5
        else:
            sample_columns = 5
            skiprows = 0

        df = pd.read_csv(uploaded_file , sep="[\t\0]",skiprows = skiprows , engine="python")
        dataframes[uploaded_file.name] = df

sample_f = st.file_uploader("csvファイルをアップロードしてください", type=["csv"])
#グラフを書く前にsample_fに即した仮データベースファイルを使用したほうが、時間早いと思われる
if sample_f is not None:
    sample_df = pd.read_csv(sample_f,encoding ='CP932')
    sample = sample_df.iloc[:,sample_columns]#DPU用 sample_columns 2 or 5

    sample_1 = sample.to_list()#DPU用 sample_columns 2 or 5
    sample_1 = [str(x) for x in sample]
    sample_2 = [x for x in sample_1 if x != "nan"]

    sample_par = sample_2

    with st.sidebar:
        x_pal=st.selectbox('x列を選択してください', sample_par)
        st.write(x_pal,"の")
        #ここでデータを読んで上下限を設定したい
        x_lower_bound = st.number_input('xの下限値と',step=1)
        x_upper_bound = st.number_input('xの上限値を入力してください',value=100,step=10) 
        
        y_pal=st.selectbox('y列を選択してｋださい', sample_par)
        st.write(y_pal,"の")        
        #ここでデータを読んで上下限を設定したい
        y_lower_bound = st.number_input('yの下限値と',step=1)
        y_upper_bound = st.number_input('yの上限値を入力してください',value=200,step=10) 

#データを読み込みグラフを作成す
#まず、サンプルファイルのみ抽出しデータを作成する　その後、表示パラメータ、上下限よりグラフ作成する
if dataframes:
    total_counts = {}#この初期化した辞書型へ読み込んで全ロードデータを保存しておく
    for filename,df in dataframes.items():
        if "Time" in df.columns and sample_columns == 5:
            df = df.iloc[1:]#dpuの場合は単位行があるために除外する 
            time_format = "%H:%M:%S.%f"
            df["Time"]= [datetime.strptime(time_str, time_format) for time_str in df["Time"]]
            init_time = df["Time"].iloc[0]
            df["Time"] = [(time - init_time).seconds for time in df["Time"]]
            df = df.apply(pd.to_numeric, errors='coerce')
        else:#windarabはカラム名調整
            new_columns=[]
            for rep in df.columns:
                rep = rep[:rep.find("[")]
                rep = rep.replace(" ","")
                new_columns.append(rep)
            df.columns = new_columns
            #df = df[sample_par]#同じカラム名にする必要あり

#分割数　10として　3Dマップを作る 10分割が１以下になる場合の処理追加必要
        z_sum = {}
        x_range = range(int(x_lower_bound), int(x_upper_bound), max(1, int((x_upper_bound - x_lower_bound) / 10)))
        y_range = range(int(y_lower_bound), int(y_upper_bound), max(1, int((y_upper_bound - y_lower_bound) / 10)))
        span_rpm = int((x_upper_bound - x_lower_bound) / 10)
        span_kl = int((y_upper_bound - y_lower_bound) / 10)
        for x in x_range:
            z_sum[x] = {}    
            for y in y_range:
                # NumPyを使用してフィルタリング
                mask_x = (df[x_pal] >= x) & (df[x_pal] < x + int((x_upper_bound - x_lower_bound) / 10))
                mask_y = (df[y_pal] >= y) & (df[y_pal] < y + int((y_upper_bound - y_lower_bound) / 10))
                filtered_data = df[mask_x & mask_y]
                z_sum[x][y] = len(filtered_data)

        dataframes[uploaded_file.name] = z_sum

#各条件での累積時間マップを作成
    #st.write(dataframes)
    if dataframes:
        total_counts = {}  # 全ファイルのデータを集約する辞書を初期化
        for filename in dataframes.keys():
            with st.sidebar:
                show_data = st.checkbox(f"{filename} を表示", value=True)
            if show_data:
                # ファイルのデータを合計
                z_sum = dataframes[filename]
                for x in z_sum:
                    if x not in total_counts:
                        total_counts[x] = {}
                    for y in z_sum[x]:
                        total_counts[x][y] = total_counts.get(x, {}).get(y, 0) + z_sum[x][y]
        # 合計結果を表示
        st.write("累積データ:")
        # 3Dプロットを作成
        fig = plt.figure(figsize=(10, 6))
        ax = fig.add_subplot(111, projection='3d')

        x_values = []
        y_values = []
        z_values = []

        for x in total_counts:
            for y in total_counts[x]:
                x_values.append(x)
                y_values.append(y)
                z_values.append(total_counts[x][y])

        ax.bar3d(x_values, y_values,0, dx=int(span_rpm/3),dy=int(span_kl/3),dz=z_values,shade=True)
        ax.set_xlabel(x_pal)
        ax.set_ylabel(y_pal)
        ax.set_zlabel('Count')
        sumall = int(z_values.sum()/3600)
        ax.set_title("{:.3f}Hr".format(sumall),fontsize="10")
        st.pyplot(fig)

     # ダウンロード用のデータを作成
        download_data = []
        for x in total_counts:
            for y in total_counts[x]:
                download_data.app
        # CSV形式でデータをダウンロード
        csv_data = pd.DataFrame(download_data, columns=[x_pal, y_pal, 'Count'])
        csv_buffer = csv_data.to_csv(index=False).encode('utf-8')

        st.download_button(
            label="元の数値データをダウンロード",
            data=csv_buffer,
            file_name='cumulative_data.csv',
            mime='text/csv'
        )
         # 一時ファイルを作成してプロットを保存
        # plt.legend(fontsize=10,loc="upper right")
        # ax1.set_title(f"Cumulative Time for {x_pal} and {y_pal}: {sumall:.3f} Hr")
                
                
                # # ax2 = fig.add_subplot(2,2,2)
                # # ax2.plot_surface(x, y, z, cmap=cm.coolwarm,linewidth=0, antialiased=False)

                # ax3 = fig.add_subplot(2, 2, 3)
                # ax3.bar(y,z)
                # ax3.set_title("30")

                # ax4 = fig.add_subplot(2, 2, 4)
                # ax4.bar(x,z)