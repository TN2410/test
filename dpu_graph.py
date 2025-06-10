 #dpuデータをstreamlitで表示する
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

st.title("dpuデータ表示")

# サンプルファイルアップロードし、選択パラメータリストを作成
sample_f = st.file_uploader("csvファイルをアップロードしてください", type=["csv"])
if sample_f is not None:
    sample_df = pd.read_csv(sample_f,encoding="CP932")
    sample_par = sample_df.iloc[:,5]#DPU用
    mylist = [str(x) for x in sample_par]
    newlist = [x for x in mylist if x != "nan"]
    with st.sidebar:
        x_pal=st.multiselect('x列を選択してください', newlist)
        y_pal=st.multiselect('y列を選択してください', newlist)
        th_pal=st.multiselect('閾値パラメータを選択', newlist)

#データファイルをアップロードし、グラフを作成する
uploaded_files = st.file_uploader("txtファイルをアップロードしてください", type="txt",accept_multiple_files=True)
if uploaded_files is not None:
    dataframes = {}#この初期化した辞書型へ読み込んで全ロードデータを保存しておく
    for uploaded_file in uploaded_files:
        df = pd.read_csv(uploaded_file,sep="[\t\0]",engine='python')
        df = df.iloc[1:]#dpuの場合は単位行があるために除外する 
        # 時間データを秒に換算する 
        time_format = "%H:%M:%S.%f"
        df["Time"]= [datetime.strptime(time_str, time_format) for time_str in df["Time"]]
        init_time = df["Time"][1]
        df["Time"] = [(time - init_time).seconds for time in df["Time"]]
        df = df.apply(pd.to_numeric)
        st.write(df[th_pal])
        max_value = df[th_pal].max()
        min_value = df[th_pal].min()
        st.write(min_value,max_value)
        with st.sidebar:
            slider1=st.slider("閾値範囲", 0,100,0, 1)
            slider2=st.slider("閾値範囲", 0,100,100, 1)
            #slider1=st.slider("閾値範囲", min_value, max_value, min_value, 1)
            #slider2=st.slider("閾値範囲", min_value, max_value, max_value, 1)
        df = df.query(slider1 < th_pal < slider2)#print(delta.seconds)
        dataframes[uploaded_file.name] = df

    #　散布図のプロット
    if dataframes:
        fig=plt.figure(figsize=(16, 9))
        # 各データフレームの表示を制御するボタンを作成
        for filename, df in dataframes.items():
            # ボタンを作成（ファイル名をボタン名として使用）
            with st.sidebar:
                show_data = st.checkbox("{} を表示".format(filename), value=True)
            # ボタンが選択されている場合に散布図をプロット
            if show_data:
                # x列とy列を指定（ここでは仮に 　'x' と 'y' 列を使用）
                selected_xdata = df[x_pal]
                selected_ydata = df[y_pal]
                #df["Time0"]=np.arange(len(df)).astype(float)
                #st.line_chart(selected_data)
                x=selected_xdata.astype(float)
                y=selected_ydata.astype(float)
                plt.scatter(x, y,label=filename)
                #plt.title(file.name)
        plt.legend(bbox_to_anchor=(1.05, 1.0), loc="upper left")
        plt.xlabel(x_pal)
        plt.ylabel(y_pal)
        st.pyplot(fig)

    #     plt.ylim(slider2, slider)
    #     plt.xlim(slider4, slider3)
    #     df["NE"][1:] = df["NE"][1:].astype(int)
    #     max_value = df["NE"][1:].max()
    #     min_value = df["NE"][1:].min()
    #     slider=st.slider("範囲", min_value, max_value, max_value, 10)
    #     slider2=st.slider("範囲", min_value, max_value, 0, 10)
    #     slider3=st.slider("範囲", min_value, max_value, max_value, 100)
    #     slider4=st.slider("範囲", min_value, max_value, 0, 100)
    #    df_ne=df[df["NE"][1:]<slider]
