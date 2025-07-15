 
#dpuデータをstreamlitで表示する
#%matplotlib inline
import os,time,gc,math,glob
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import re
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.gridspec import GridSpec
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

 #windarab と　dpu　ファイルの差を自動検知して、サンプルを変更する
st.set_page_config(
     page_title="PLOT",  
     layout="wide", 
     initial_sidebar_state="expanded")
st.title("windarab or dpu 積算データ")

@st.cache_data
def load_uploaded_file(uploaded_file, skiprows):
    return pd.read_csv(uploaded_file, sep="[\t\0]", skiprows=skiprows, engine="python")

st.markdown(
    """
    <style>
    .custom-uploader {
        width: 200px;  /* アップローダの幅 */
        height: 400px; /* アップローダの高さ */
    }
    .custom-selectbox {
        width: 400px;  /* セレクトボックスの幅 */
    }
    </style>
    """,
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)

with col1:
    uploaded_files = st.file_uploader("txtファイルをアップロードしてください(先)", type="txt",accept_multiple_files=True 
                                 )
specific_string = "windarab"  # ここに検索したい文字を設定
if uploaded_files is not None:
    sample_columns, skiprows = None, None
    dataframes = {}
    for uploaded_file in uploaded_files:
       #ファイルを簡易的に読み込んでwindarabデータを　5行削除する
        initial_lines = pd.read_csv(uploaded_file, nrows=2)
     # ファイルを再度読み込むために、元のファイルポインタを最初に戻す
        uploaded_file.seek(0)
        if initial_lines.apply(lambda x: x.astype(str).str.contains(specific_string).any(), axis=1).any():
            sample_columns = 2
            skiprows = 5
        else:
            sample_columns = 5
            skiprows = 0

        df = pd.read_csv(uploaded_file , sep="[\t\0]",skiprows = skiprows , engine="python")
        dataframes[uploaded_file.name] = df

with col2:
    sample_f = st.file_uploader("csvファイルをアップロードしてください", type=["csv"])

#グラフを書く前にsample_fに即した仮データベースファイルを使用したほうが、時間早いと思われる
if sample_f is not None:
    sample_df = pd.read_csv(sample_f,encoding ='CP932')
    sample = sample_df.iloc[:,sample_columns]#DPU用 sample_columns 2 or 5

    sample_1 = sample.to_list()#DPU用 sample_columns 2 or 5
    sample_1 = [str(x) for x in sample]
    sample_2 = [x for x in sample_1 if x != "nan"]

    sample_par = sample_2

    with st.sidebar:
        x_pal=st.selectbox('x列を選択してください', sample_par )
        st.write(x_pal,"の")
        #ここでデータを読んで上下限を設定したい
        if x_pal == "NE" or x_pal == "nmot": 
            max_x_value = 8000
        else:
            max_x_value = 100
        x_lower_bound = st.number_input('xの下限値と',step=1)
        x_upper_bound = st.number_input('xの上限値を入力してください', value = max_x_value , step=10) 
        
        y_pal=st.selectbox('y列を選択してください', sample_par )
        st.write(y_pal,"の")        
        #ここでデータを読んで上下限を設定したい
        y_lower_bound = st.number_input('yの下限値と',step=1)
        y_upper_bound = st.number_input('yの上限値を入力してください', value = 200 , step=10) 

        x_div_num = st.number_input('x軸分割数', value = 20)
        y_div_num = st.number_input('y軸分割数', value = 20)

if dataframes:
    total_counts = {}#この初期化した辞書型へ読み込んで全ロードデータを保存しておく
    
    #データ積算とグラフを作成する

    z_sum = {}#チェックボックスにチェックが入っている場合の)#チェックボックスにチェックが入っている場合のみプロットする
    fig = make_subplots(
    rows=1, 
    cols=2, 
    specs=[[{"type": "surface"}, {"type": "scatter"}]],  # 1つ目は2Dプロット、2つ目は3Dプロット
    subplot_titles=("3D_Scatter", "Scatter Plot"),
    horizontal_spacing=0.1  # グラフ間の水平スペースを調整
    )

    for filename, df in dataframes.items():
        with st.sidebar:
            show_data = st.checkbox("{} を表示".format(filename), value=True)        
        # 合計結果を表示
        if show_data:# DataFrameが空でないことを確認
            if df.empty:
                st.warning(f"{filename} は空のファイルです。")
                continue    
            if "Time" in df.columns and sample_columns == 5:
                df = df.iloc[1:]#dpuの場合は単位行があるために除外する 
                time_format = "%H:%M:%S.%f"
                df["Time"]= [datetime.strptime(time_str, time_format) for time_str in df["Time"]]
                init_time = df["Time"].iloc[0]
                df["Time"] = [(time - init_time).seconds for time in df["Time"]]
                df = df.apply(pd.to_numeric, errors='coerce')
            else:#windarabはカラム名調整
                new_columns=[]
                for rep in df.columns:
                    rep = rep[:rep.find("[")]
                    rep = rep.replace(" ","")
                    new_columns.append(rep)
                df.columns = new_columns
                #df = df[sample_par]#同じカラム名にする必要あり
            fig.add_trace(go.Scatter(x=df[x_pal], y=df[y_pal], 
            mode='markers', name = filename),
            row=1,
            col=2,
            )    

    #分割数　10として　3Dマップを作る 10分割が１以下になる場合の処理追加必要
        
            x_span = (x_upper_bound - x_lower_bound)/x_div_num
            y_span = (y_upper_bound - y_lower_bound)/y_div_num    
            
            for xx in range(x_div_num):
                x = xx * x_span + int(x_lower_bound)
                z_sum[x] = {}    
                for yy in range(y_div_num):
                    y = yy * y_span + int(y_lower_bound)
                    # NumPyを使用してフィルタリング
                    mask_x = (df[x_pal] >= x) & (df[x_pal] < x + x_span)
                    mask_y = (df[y_pal] >= y) & (df[y_pal] < y + y_span)
                    filtered_data = df[mask_x & mask_y]
                    z_sum[x][y] = len(filtered_data)

            # z_sumを total_counts に追加
            for x in z_sum:
                if x not in total_counts:
                    total_counts[x] = {}
                for y in z_sum[x]:
                    total_counts[x][y] = total_counts.get(x, {}).get(y, 0) + z_sum[x][y]

    x_values = []
    y_values = []
    z_values = []

    for x in total_counts:
        for y in total_counts[x]:
            x_values.append(x)
            y_values.append(y)
            z_values.append(total_counts[x][y])

    for i in range(len(x_values)):
        fig.add_trace(go.Scatter3d(
            x=[x_values[i], x_values[i], x_values[i]],
            y=[y_values[i], y_values[i], y_values[i]],
            z=[0, z_values[i] , 0],
            mode='lines',
            line=dict(width=10,color = "blue"),
            showlegend = False
            ),
            row=1,
            col=1)    

    # 3D散布図の軸ラベル設定
    sumall = sum(z_values)/3600
   # 各サブプロットの幅を比率3:7に設定
    #fig['layout']['xaxis'].update(domain=[0, 0.7])  # 1つ目のグラフの幅
    #fig['layout']['xaxis'].update(domain=[0.7, 1])  # 2つ目のグラフの幅 
     

    fig.update_layout(
        title = "全 {:.3f} Hr".format(sumall),
        scene = dict(
        xaxis_title= x_pal,
        yaxis_title= y_pal,
        zaxis_title= "Time(sec)",
        xaxis=dict(range=[x_lower_bound,x_upper_bound]),  # X 軸の上下限
        yaxis=dict(range=[y_lower_bound,y_upper_bound]),  # Y 軸の上下限
           # Z 軸の上下限
        ),
        scene2 = dict(
        xaxis_title= x_pal,
        yaxis_title= y_pal,
        xaxis=dict(range=[x_lower_bound,x_upper_bound]),  # X 軸の上下限
        yaxis=dict(range=[y_lower_bound,y_upper_bound])
        ),
        height = 900 ,
        width = 1200 ,
    )
    # 2D グラフのタイトルと軸ラベルを設定

    fig.update_layout(legend=dict(
    orientation="v",  # 水平に配置
    yanchor="bottom",
    y=1.05 ,  # グラフの上側に配置
    xanchor="center",
    x=0.1
     ) , # 左よりに配置
    )

    # 凡例の設定: 左のグラフにのみ凡例を表示
    fig.update_layout(
        showlegend=True,
    )

    # 右側のグラフの凡例を非表示にする
    fig['data'][1]['showlegend'] = False  # 2つ目のプロットの凡例を非表示に
    
    if 'show_graph' not in st.session_state:
        st.session_state.show_graph = False

# ボタンの作成
    if st.button('グラフを表示/非表示'):
        st.session_state.show_graph = not st.session_state.show_graph

# グラフの表示
    if st.session_state.show_graph:
        st.plotly_chart(fig , use_container_width=False)

    # ダウンロード用のデータを作成
    download_data = []
    for x in total_counts:
        for y in total_counts[x]:
            download_data.append([x, y, total_counts[x][y]])
    # CSV形式でデータをダウンロード
    csv_data = pd.DataFrame(download_data, columns=[x_pal, y_pal, 'Count'])
    csv_buffer = csv_data.to_csv(index=False).encode('utf-8')

    st.download_button(
        label="積算データをダウンロード",
        data=csv_buffer,
        file_name='cumulative_data.csv',
        mime='text/csv'
    )
