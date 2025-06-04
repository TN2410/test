import os,time,gc,math,glob
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#import japanize_matplotlib

st.title("振動とPmax周波数の相関")

with st.sidebar:
    st.title("レンジなど調整用")
    min_value=0
    max_value=5000
    max_amp=1000
    min_freq=st.slider("下限周波数", min_value, max_value, 1200, 100)
    max_freq=st.slider("上限周波数", min_value, max_value, 1500, 100)
    maxamp=st.slider("上限AMP", 0, max_amp, 10, 2)
    cyl_amp=st.slider("cyl_amp倍率", 0, 1000, 1000, 100)

with st.expander("アップロード"):
    uploaded_files = st.file_uploader("accum.CSVファイルをアップロード(複数可)", type="csv",accept_multiple_files=True)
#st.write("check22")
#df_ne=df[df["NE"][1:]<slider]
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
            columns=st.slider("時間", 0, len(df.columns), 50, 1)

        fig=plt.figure(figsize=(10, 4))
# 各データフレームの表示を制御するボタンを作成
        x=np.arange(len(df.columns)-1).astype(float)
        y=df.columns[1:].astype(float)
        st.write(x)
        st.write(y)
        plt.plot(x, y)
        plt.scatter(columns,y[columns],color="red")
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
                plt.ylim(0, maxamp)
                plt.xlim(min_freq, max_freq)
                #plt.title(file.name)
        plt.legend(bbox_to_anchor=(1.05, 1.0), loc="upper left")
        plt.xlabel("freq(Hz)")
        plt.ylabel("G")
        st.pyplot(fig)

#        st.write(df.iloc[:5,0])
#        st.write(df.iloc[:5,0])



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


