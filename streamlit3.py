#FFT 累積データをフォルダ選択で自動計算する

#%matplotlib inline
import os,time,gc,math,glob
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
x_pal=st.multiselect('x列を選択してください', ["NE","EXT_R"])
y_pal=st.multiselect('y列を選択してください', ["NE","EXT_R"])

f = st.file_uploader("txtファイルをアップロードしてください", type="txt",accept_multiple_files=True)

if f is not None:


    for file in f:
        df = pd.read_csv(file,sep="[\t\0]",index_col=0)
        st.write("アップロードされたファイル:")
        #st.write(df)
#f=r"C:\Users\1219829\Desktop\python\streamlit\ff.csv"
# ファイルがアップロードされた場合
    #フォルダ名とチェックボックスを表示


        selected_xdata = df[x_pal]
        selected_ydata = df[y_pal]
        df["Time0"]=np.arange(len(df)).astype(float)
        #st.line_chart(selected_data)
        x=selected_xdata[1:].astype(float)
        y=selected_ydata[1:].astype(float)
   
        fig=plt.figure()
        plt.scatter(x, y)
        plt.title("scatter")
        plt.xlabel(x_pal)
        plt.ylabel(y_pal)
        st.pyplot(fig)
        st.button("Process A", on_click=process_a)
        st.button("Process B", on_click=process_b)

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

