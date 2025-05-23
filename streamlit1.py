import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

fig=plt.figure()

# 緯度経度データ（10進数）
pref_list = [
  {"longitude":135.741667, "latitude":30.789828}, # 熊本県
  {"longitude":131.423855, "latitude":31.911090}, # 宮崎県
  {"longitude":130.557981, "latitude":31.560148}, # 鹿児島県
]
st.map(pref_list)
st.number_input("input_your_number")  
# チェックボックス
st.checkbox("CHECK") 
if st.button("bot", key='my_button', help='このボタンをクリックしてアクションを実行します'):
   st.write('ボタンがクリックされました！')

#入力値でカラム名を指定し、グラフを書く。dpuとのメリット複数のファイルを表示可能か？。
year=st.number_input('年(1952~5年おき)',1952,2007,1952,step=5)
#df_px=df[df['year'] ==year]