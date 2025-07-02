 
#dpuデータをstreamlitで表示する
#%matplotlib inline
import os,time,gc,math,glob
import streamlit as st
import pandas as pd
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
uploaded_files = st.file_uploader("txtファイルをアップロードしてください(先)", type="txt",accept_multiple_files=True 
                                 )
specific_string = "windarab"  # ここに検索したい文字を設定
if uploaded_files is not None:
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
if uploaded_files is not None:
    dataframes = {}#この初期化した辞書型へ読み込んで全ロードデータを保存しておく
    for uploaded_file in uploaded_files:
        df = pd.read_csv(uploaded_file , sep="[\t\0]",skiprows = skiprows , engine="python")
        if sample_columns == 5:
            df = df.iloc[1:]#dpuの場合は単位行があるために除外する 
            #df = df[sample_par]
            if "Time" in df.columns:#DPU限定処理
                time_format = "%H:%M:%S.%f"
                df["Time"]= [datetime.strptime(time_str, time_format) for time_str in df["Time"]]
                init_time = df["Time"].iloc[0]
                df["Time"] = [(time - init_time).seconds for time in df["Time"]]
                df = df.apply(pd.to_numeric)
        else:#windarabはカラム名調整
            new_columns=[]
            for rep in df.columns:
                rep = rep[:rep.find("[")]
                rep = rep.replace(" ","")
                new_columns.append(rep)
            df.columns = new_columns
            #df = df[sample_par]#同じカラム名にする必要あり

#分割数　10として　3Dマップを作る
        for x in range(int(x_lower_bound),int(x_upper_bound),int((x_upper_bound-x_lower_bound)/10)):
            for y in range(int(y_lower_bound),int(y_upper_bound),int((y_upper_bound-y_lower_bound)/10)):
                x_query_string = f"{x_pal} >= {x} & {x_pal} < {x + int((x_upper_bound-x_lower_bound)/10)}"
                y_query_string = f"{y_pal} >= {y} & {y_pal} < {y + int((y_upper_bound-x_lower_bound)/10)}"
                x_filtered_data = df.query(x_query_string)
                y_filtered_data = x_filtered_data.query(y_query_string)
                ####以下に記載できている？
                dataframes[uploaded_file.name,x,y] = len(y_filtered_data)
                st.write(dataframes)
                st.write(len(y_filtered_data))

#各条件での累積時間マップを作成
    #st.write(dataframes)
    if dataframes:
        total_counts = {}  # 全ファイルのデータを集約する辞書を初期化
        
        fig=plt.figure(figsize=(10, 6))
        # 各データフレームの表示を制御するボタンを作成

        for filename in dataframes.items():
            # ボタンを作成（ファイル名をボタン名として使用）
            with st.sidebar:
                show_data = st.checkbox("{} を表示".format(filename), value=True)
            # ボタンが選択されている場合に散布図をプロット
            if show_data:
                if (x, y) not in total_counts:
                    total_counts[(x, y)] = 0
                for x,y in dataframes.items():
                    total_counts[(x, y)] + = dataframes[x,y]  # 各ファイルのカウントを
                    st.write(total_count)
            z = int(total_counts[(x,y)]/3600)# x列とy列を指定（ここでは仮に 'x' と 'y' 列を使用）
                #df["Time0"]=np.arange(len(df)).astype(float)   
                # plt.xlabel(th_pal)
                # plt.legend(fontsize=10,loc="upper right")
                # plt.ylabel("Time(sec)")    
                # axをfigureに設定

        # 3Dグラフ用のデータを準備
        x_positions = []
        y_positions = []
        z_values = []

        for (x, y), z in total_counts.items():
            x_positions.append(x)
            y_positions.append(y)
            z_values.append(z)

        # 3Dバーグラフの描画
        ax1 = fig.add_subplot(1, 1, 1, projection='3d')
        ax1.bar3d(x_positions, y_positions, [0] * len(z_values), dx=0.4, dy=0.4, dz=z_values, shade=True)
        ax1.set_title(f"Cumulative Time for {x_pal} and {y_pal}: {sumall:.3f} Hr")
        ax1.set_xlabel(x_pal)
        ax1.set_ylabel(y_pal)
        ax1.set_zlabel("Count")
                # ax1 = fig.add_subplot(2, 2, 1, projection='3d')
                # ax1.bar3d(x, y, 0, dx=0.4, dy=0.5 , dz=z , shade=True)
                # ax1.set_title("10")
                # ax1.set_title("{}_{:.3f}Hr_{}=<{}<{}".format(y_pal,sumall,x_lower_bound,y_pal,x_upper_bound),fontsize="10")
                
                # # ax2 = fig.add_subplot(2,2,2)
                # # ax2.plot_surface(x, y, z, cmap=cm.coolwarm,linewidth=0, antialiased=False)

                # ax3 = fig.add_subplot(2, 2, 3)
                # ax3.bar(y,z)
                # ax3.set_title("30")

                # ax4 = fig.add_subplot(2, 2, 4)
                # ax4.bar(x,z)

        st.pyplot(fig)
