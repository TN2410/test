 
#dpuデータをstreamlitで表示する
#%matplotlib inline
import os,time,gc,math,glob
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import re
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
        y_pal=st.multiselect('y列を選択してください', sample_par) 
        th_pal=st.selectbox('閾値パラメータを選択', sample_par)
        st.write(th_pal,"の")


        #ここでデータを読んで上下限を設定したい
        lower_bound = st.number_input('の下限値と',step=1)
        upper_bound = st.number_input('上限値を入力してください',value=100,step=1) 

#データを読み込みグラフを作成すｒ
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
        
        max_value = int(df[th_pal].max())
        min_value = int(df[th_pal].min())
        query_string = f"{th_pal} >= @lower_bound & {th_pal} < @upper_bound"    
        filtered_data = df.query(query_string)
        dataframes[uploaded_file.name] = filtered_data
    #st.write(dataframes)
    if dataframes:
        fig=plt.figure(figsize=(10, 6))
        # 各データフレームの表示を制御するボタンを作成
        sumall = 0
        for filename, filtered_data in dataframes.items():
            # ボタンを作成（ファイル名をボタン名として使用）
            with st.sidebar:
                show_data = st.checkbox("{} を表示".format(filename), value=True)
            # ボタンが選択されている場合に散布図をプロット
            if show_data:
                # x列とy列を指定（ここでは仮に 'x' と 'y' 列を使用）
                selected_ydata = filtered_data[y_pal]
                selected_zdata = filtered_data[th_pal]
                #df["Time0"]=np.arange(len(df)).astype(float)
                x = str(filename.replace(".txt",""))
                y = len(selected_ydata[1:])
                y2 = selected_ydata[1:]
                z = selected_zdata[1:]
                
                sumall += len(selected_ydata[1:])/3600

                # plt.subplot(1,2,1)
                # plt.scatter(z,y2)
                # plt.ylabel(y_pal)
                # plt.xlabel(th_pal)
                # plt.legend(fontsize=10,loc="upper right")
                
                # plt.subplot(1,2,2)
                # plt.bar(x, y)
                # plt.ylabel("Time(sec)")
                # plt.title("{}_{:.3f}Hr_{}=<{}<{}".format(y_pal,sumall,lower_bound,th_pal,upper_bound),fontsize="10")

                ax = fig.add_subplot(projection='3d')
                ax.bar(1,1,1, color='blue')

        st.pyplot(fig)