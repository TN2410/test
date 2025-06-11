 
#dpuデータをstreamlitで表示する
#%matplotlib inline
import os,time,gc,math,glob
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
# windarab と　dpu　ファイルの差を自動検知して、サンプルを変更する

st.set_page_config(
    page_title="PLOT",  
    layout="wide", 
    initial_sidebar_state="auto")

st.title("windarab or dpu データ表示")

uploaded_files = st.file_uploader("txtファイルをアップロードしてください(先)", type="txt"#,accept_multiple_files=True
                                  )
if uploaded_files is not None:
    dataframes = {}#この初期化した辞書型へ読み込んで全ロードデータを保存しておく
    for uploaded_file in uploaded_files:
       #ファイルを簡易的に読み込んでwindarabデータを　5行削除する
        #df0 = pd.read_csv(uploaded_file,sep="\t",encoding="CP932",nrows=1)
        df = pd.read_csv(uploaded_file)
        st.write(df0.columns[0:3])
        if df0.columns.empty:
            st.warning("カラム名取得できず")
            continue
        if "BOSCH-DARAB" in df0.columns[0]: 
            skiprowsno = 0
            sample_columns = 2
            df = pd.read_csv(uploaded_file,encoding ='CP932',#skiprows=skiprowsno
                             #low_memory=False
                             )#windarabは５ dpuはskiprowsなし
            st.write(df)
        else:
            skiprows = 0
            sample_columns = 5
            df = pd.read_csv(uploaded_file,sep="\t\0",engine="python",encoding="utf-8")
            dataframes[uploaded_file.name] = df
        st.write(df)##########カラム名が表示されない
        if "Time" in df.columns:
            time_format = "%H:%M:%S.%f"
            df["Time"][1:] = [datetime.strptime(time_str, time_format) for time_str in df["Time"][1:]]
            init_time = df["Time"][1]
            df["Time"][1:] = [(time - init_time).seconds for time in df["Time"][1:]]
            st.write(df["Time"][1:])

        st.write(skiprows)

sample_f = st.file_uploader("csvファイルをアップロードしてください", type=["csv"])
if sample_f is not None:
    sample_df = pd.read_csv(sample_f,encoding ='CP932')
    sample_par = sample_df.iloc[:,sample_columns]#DPU用 sample_columns 2 or 5
    mylist = [str(x) for x in sample_par]
    newlist = [x for x in mylist if x != "nan"]
    with st.sidebar:
        x_pal=st.multiselect('x列を選択してください', newlist)
        y_pal=st.multiselect('y列を選択してください', newlist)  
    if dataframes:
        fig=plt.figure(figsize=(10, 6))
        # 各データフレームの表示を制御するボタンを作成
        for filename, df in dataframes.items():
            # ボタンを作成（ファイル名をボタン名として使用）
            with st.sidebar:
                show_data = st.checkbox("{} を表示".format(filename), value=True)
            # ボタンが選択されている場合に散布図をプロット
            if show_data:
                # x列とy列を指定（ここでは仮に 'x' と 'y' 列を使用）
                st.write(df.columns)
                selected_xdata = df[x_pal]
                selected_ydata = df[y_pal]
                #df["Time0"]=np.arange(len(df)).astype(float)
                #st.line_chart(selected_data)
                x=selected_xdata[1:].astype(float)
                y=selected_ydata[1:].astype(float)
                plt.scatter(x, y,label=filename)
                #plt.title(file.name)
        plt.legend(bbox_to_anchor=(1.05, 1.0), loc="upper left")
        plt.xlabel(x_pal)
        plt.ylabel(y_pal)
        st.pyplot(fig)