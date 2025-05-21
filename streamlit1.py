import streamlit as st

# 緯度経度データ（10進数）
pref_list = [
  {"longitude":135.741667, "latitude":30.789828}, # 熊本県
  {"longitude":131.423855, "latitude":31.911090}, # 宮崎県
  {"longitude":130.557981, "latitude":31.560148}, # 鹿児島県
]

st.map(pref_list)
X="1"
if st.button(x, key='my_button', help='このボタンをクリックしてアクションを実行します'):
   st.write('ボタンがクリックされました！')