import os,time,gc,math,glob
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="PLOT",  
    layout="wide", 
    initial_sidebar_state="auto")

st.title("振動とPmax周波数の相関")

with st.sidebar:
    st.title("レンジなど調整用")
    min_value=0
    max_value=5000
    max_amp=1000
    min_freq=st.slider("下限周波数", min_value, max_value, 0, 50)
    max_freq=st.slider("上限周波数", min_value, max_value, 150, 50)
    minamp=st.slider("下限AMP", 0, max_amp, 0, 5)
    maxamp=st.slider("上限AMP", 0, max_amp, 30, 5)
    cyl_amp=st.slider("cyl_amp倍率", 0, 1000, 1, 25)

with st.expander("アップロード"):
    uploaded_files = st.file_uploader("accum.CSVファイルをアップロード(複数可)", type="csv",accept_multiple_files=True)
# ファイルがアップロードされた場合
if uploaded_files is not None:
    dataframes = {}
#この初期化した辞書型へ読み込んで全ロードデータを保存しておく
    for uploaded_file in uploaded_files:
        df = pd.read_csv(uploaded_file)
        dataframes[uploaded_file.name] = df
    #　散布図のプロット
        df=df.astype(float)
        #color = st.color_picker('Pick A Color', '#00f900')



    if dataframes:
        with st.sidebar:
            columns=st.slider("時間", 0, len(df.columns), 61, 1)

        # 時間軸のb場所と回転数を表示
        fig=plt.figure(figsize=(10, 4))
        x=np.arange(len(df.columns)-1).astype(float)
        y=df.columns[1:].astype(float)
        plt.plot(x, y)
        plt.scatter(columns,y[columns],color="red",s=20)
        plt.xlabel("time")
        plt.ylabel("rpm")
        st.pyplot(fig)
        
        fig=plt.figure(figsize=(10, 6))
        # 各データフレームの表示を制御するボタンを作成
        for filename, df in dataframes.items():
            # ボタンを作成（ファイル名をボタン名として使用）
            with st.sidebar:
                show_data = st.checkbox("{} を表示".format(filename), value=True)

            # ボタンが選択されている場合に散布図をプロット
            if show_data:
                # x列とy列を指定（ここでは仮に 'x' と 'y' 列を使用）
                selected_xdata = df.iloc[:,0]*1.5625
                if "_Cyl_" in filename:
                    selected_ydata = df.iloc[:,columns]*cyl_amp
                else:
                    selected_ydata = df.iloc[:,columns]
                #df["Time0"]=np.arange(len(df)).astype(float)
                #st.line_chart(selected_data)
                x=selected_xdata[1:].astype(float)
                y=selected_ydata[1:].astype(float)
                plt.plot(x, y,label=filename)
                plt.ylim(minamp, maxamp)
                plt.xlim(min_freq, max_freq)
                #plt.title(file.name)
        plt.legend(bbox_to_anchor=(1.05, 1.0), loc="upper left")
        plt.xlabel("freq(Hz)")
        plt.ylabel("G")
        st.pyplot(fig)


