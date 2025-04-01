#FFT 累積データをstreamlitで表示する
import sys
sys.path.append(r'c:\users\1219829\python\py312\lib\site-packages')
sys.path.append(r'C:\Users\1219829\python\Py312\Scripts')
sys.path.append(r'C:\Users\1219829\AppData\Local\Programs\Python\Python312\Scripts')
                
import os
import pandas as pd
import streamlit as st

dirname = r'C:\Users\1219829\OneDrive - トヨタ自動車株式会社\○開発資料\WEC\FFT\DYNO_TEST\P0053\202503_PdSFTFr差\317_Dyno_File_0005_404_2025_HPP RH Z_accum_400.csv'

#df=pd.read_csv(dirname, encoding='utf-8',skiprows=0)#ベースデータの読み込み
#print(len(df.columns))

#t =0.8 * np.array(range(len(df.columns)-1))
#最上行のカラム名を数値化し　neと定義する
#ne=df.columns[1:].astype(float)
#回転数×時間のグラフ
#plt.plot(t,ne)
#plt.show()

st.slider(0,500)

#全時間窓の代表回転数と周波数分析結果
#for j in range(1,len(df.columns)):
    
#    x=df.iloc[:,0]
#    y=df.iloc[:,j]
    
#    plt.plot(x,y)
#    plt.show()

# st.session_state
# st.write
# st.json
# st.data_editer
# st.columns
# st.empty
# st.container
# st.button(callback)
# st.spinner
# st.expander
# st.slidebar
# st.swith