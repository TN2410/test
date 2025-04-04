import sys

sys.path.append(r'C:\Users\1219829\AppData\Local\Programs\Python\Python312\python312.zip')
sys.path.append(r'C:\Users\1219829\AppData\Local\Programs\Python\Python312\DLLs')
sys.path.append(r'C:\Users\1219829\AppData\Local\Programs\Python\Python312\Lib')
sys.path.append(r'C:\Users\1219829\AppData\Local\Programs\Python\Python312')
sys.path.append(r'C:\Users\1219829\AppData\Local\Programs\Python\Python312\Lib\site-packages')
sys.path.append(r'C:\Users\1219829\AppData\Local\Programs\Python\Python312\Lib\site-packages\win32')
sys.path.append(r'C:\Users\1219829\AppData\Local\Programs\Python\Python312\python312.zip')
sys.path.append(r'C:\Users\1219829\AppData\Local\Programs\Python\Python312\Lib\site-packages\win32\lib')
sys.path.append(r'C:\Users\1219829\AppData\Local\Programs\Python\Python312\Lib\site-packages')


import streamlit as st
import pandas as pd
import numpy as np
import os


#FFT 累積データをstreamlitで表示する
# ファイルアップロード

f = st.file_uploader("CSVファイルをアップロードしてください", type="csv")

# ファイルがアップロードされた場合
if f is not None:
    df = pd.read_csv(f,index_col=0)
    st.write("アップロードされたデータフレーム:")
    st.write(df)

    time=np.arange(0,8192,1)

    st.scatter_chart(df,x="freq",y="max")
	

    #plt.xlim(0.5, 12.5)
    #plt.ylim(0, 40)


    age = st.slider("ファイルを選択してください",0,800,20)
    age = st.slider("ファイルを選択してください",0,100,20)