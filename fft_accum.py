import os,time,gc,math,glob
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

f = st.file_uploader("accumCSVファイルをアップロードしてください", type="csv",accept_multiple_files=True)
st.write("check")

# ファイルがアップロードされた場合
if f is not None:
    dataframes = {}
#この初期化した辞書型へ読み込んで全ロードデータを保存しておく
    for uploaded_file in uploaded_files:
        df = pd.read_csv(uploaded_file,index_col=0)
        dataframes[uploaded_file.name] = df
    #　散布図のプロット
    	df=df.astype(float)
        color = st.color_picker('Pick A Color', '#00f900')

    if dataframes:
        fig=plt.figure(figsize=(10, 6))
        # 各データフレームの表示を制御するボタンを作成
        for filename, df in dataframes.items():
            # ボタンを作成（ファイル名をボタン名として使用）
            show_data = st.checkbox("{} を表示".format(filename), value=True)
            # ボタンが選択されている場合に散布図をプロット
            if show_data:
                # x列とy列を指定（ここでは仮に 'x' と 'y' 列を使用）
                selected_xdata = df.iloc[:,0]
                selected_ydata = df.iloc[:,0]
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


    #     df = df.T
    # #グラフ用に振幅最大値を算出
    #     amax = df.max().max()#周波数と時間軸のスライダに応じて最大値を出したい
    #     df['Time'] = np.arange(0,int(len(df)))#時間軸は窓長さに変化する必要あり
    #     df['Time'] = df['Time'].astype(int)
    #     df["NE"] =list(df.index)
    #     df["NE"] = df["NE"].astype(float)
    #     #option = st.selectbox('日付',list(range(1, 32)))

    #     slider=st.slider("範囲", 0, len(df), 0, 1)
    #     slider2=st.slider("下限周波数", 0, 5000, 0, 100)
    #     slider3=st.slider("上限周波数", 0, 5000, 0, 100)

    #     #指定回転数の色を分ける
    #     st.scatter_chart(df,x='Time',y="NE",color=(60,0,255))


