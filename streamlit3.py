#FFT 累積データをフォルダ選択で自動計算する

#%matplotlib inline
import os,time,gc,math,glob,re
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt

def process_a():
    st.write("Processing A...")

def process_b():
    st.write("Processing B...")

# 複数のファイルを読み込んでから処理する

sample_f = st.file_uploader("txtファイルをアップロードしてください", type="csv")
if sample_f is not None:
    sample_df = pd.read_csv(sample_f,encoding="CP932")
    sample_par = sample_df.iloc[:,5]
    mylist = [str(x) for x in sample_par]
    newlist = [x for x in mylist if x != "nan"]
    x_pal=st.multiselect('x列を選択してください', newlist)
    y_pal=st.multiselect('y列を選択してください', newlist)

uploaded_files = st.file_uploader("txtファイルをアップロードしてください", type="txt",accept_multiple_files=True)
if f is not None:
    dataframes = {}
    for uploaded_file in uploaded_files:
        df = pd.read_csv(uploaded_file,sep="[\t\0]",index_col=0)
        dataframes[uploaded_file.name] = df

# 散布図のプロット
        if dataframes:
            fig=plt.figure(figsize=(10, 6))
            # 各データフレームの表示を制御するボタンを作成
            for filename, df in dataframes.items():
                # ボタンを作成（ファイル名をボタン名として使用）
                show_data = st.checkbox(f'{filename} を表示', value=True)
                
                # ボタンが選択されている場合に散布図をプロット
                if show_data:
                    # x列とy列を指定（ここでは仮に 'x' と 'y' 列を使用）
        
                    selected_xdata = df[x_pal]
                    selected_ydata = df[y_pal]
                    df["Time0"]=np.arange(len(df)).astype(float)
                    #st.line_chart(selected_data)
                
                    x=selected_xdata[1:].astype(float)
                    y=selected_ydata[1:].astype(float)

                    plt.scatter(x, y,label=filename)
                    #plt.title(file.name)
            plt.legend(bbox_to_anchor=(1.05, 1.0), loc="upper left")
            plt.xlabel(x_pal)
            plt.ylabel(y_pal)
            st.pyplot(fig)

    #     plt.ylim(slider2, slider)
    #     plt.xlim(slider4, slider3)

    # #smpファイルよりチェックRAM名を読み取り
    # #結果表示
    #     df["NE"][1:] = df["NE"][1:].astype(int)
    #     max_value = df["NE"][1:].max()
    #     min_value = df["NE"][1:].min()

    #     df["Time"] = np.arange(len(df))

    #     slider=st.slider("範囲", min_value, max_value, max_value, 10)
    #     slider2=st.slider("範囲", min_value, max_value, 0, 10)
    #     slider3=st.slider("範囲", min_value, max_value, max_value, 100)
    #     slider4=st.slider("範囲", min_value, max_value, 0, 100)

    #    df_ne=df[df["NE"][1:]<slider]
    #　　データフレーム操作必要
    #
    #   st.scatter_chart(df,x="Time",y="NE")
    #グラフの表示変更はOK


        # if st.checkbox(testtest):
        #     st.write('グラフを表示する')
        #     st.pyplot(fig)

