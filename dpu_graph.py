 
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
if sample_f is not None:
    sample_df = pd.read_csv(sample_f,encoding ='CP932')
    sample_par = sample_df.iloc[:,sample_columns]#DPU用 sample_columns 2 or 5
    mylist = [str(x) for x in sample_par]
    newlist = [x for x in mylist if x != "nan"]
    with st.sidebar:
        y_pal=st.multiselect('y列を選択してください', newlist) 
        th_pal=st.selectbox('閾値パラメータを選択', newlist)
        st.write(th_pal,"の")
        lower_bound = st.number_input('の下限値と',step=1)
        upper_bound = st.number_input('上限値を入力してください',value=100,step=1) 

#どれをチェックボックス選択しても最後に読み込んだ一つしか表示されない
if uploaded_files is not None:
    dataframes = {}#この初期化した辞書型へ読み込んで全ロードデータを保存しておく
    for uploaded_file in uploaded_files:
        df = pd.read_csv(uploaded_file , sep="[\t\0]",skiprows = skiprows , engine="python")
        if sample_columns == 5:
            df = df.iloc[1:]#dpuの場合は単位行があるために除外する 
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
        
        max_value = int(df[th_pal].max())
        min_value = int(df[th_pal].min())
        query_string = f"{th_pal} >= @lower_bound & {th_pal} <= @upper_bound"    
        filtered_data = df.query(query_string)
        dataframes[uploaded_file.name] = filtered_data
    #st.write(dataframes)
    if dataframes:
        fig=plt.figure(figsize=(10, 6))
        # 各データフレームの表示を制御するボタンを作成
        for filename, filtered_data in dataframes.items():
            # ボタンを作成（ファイル名をボタン名として使用）
            with st.sidebar:
                show_data = st.checkbox("{} を表示".format(filename), value=True)
            # ボタンが選択されている場合に散布図をプロット
            if show_data:
                # x列とy列を指定（ここでは仮に 'x' と 'y' 列を使用）
                selected_ydata = filtered_data[y_pal]
                #df["Time0"]=np.arange(len(df)).astype(float)
                #st.line_chart(selected_data)
                y=len(selected_ydata[1:])
                plt.bar(filename, y)
                #plt.title(file.name)
        plt.legend(bbox_to_anchor=(1.05, 1.0), loc="upper left")
        plt.title("y_pal",font="20")
        plt.ylabel(y_pal)
        st.pyplot(fig)