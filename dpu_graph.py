 
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
from scipy import stats

 #windarab と　dpu　ファイルの差を自動検知して、サンプルを変更する
st.set_page_config(
     page_title="PLOT",  
     layout="wide", 
     initial_sidebar_state="expanded")
st.title("windarab or dpu 積算データ")

@st.cache_data
def load_uploaded_file(uploaded_file, skiprows):
    return pd.read_csv(uploaded_file, sep="[\t\0]", skiprows=skiprows, engine="python")

col1, col2 ,col3 = st.columns(3)

with col1:
    uploaded_files = st.file_uploader("txtファイルをアップロードしてください(先)", type="txt",accept_multiple_files=True
with col2:
    uploaded_files2 = st.file_uploader("別のtxtファイルをアップロードしてください", type="txt", accept_multiple_files=True)
    dataframes2 = {} 
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

with col3:
    sample_f = st.file_uploader("csvファイルをアップロードしてください", type=["csv"])

#グラフを書く前にsample_fに即した仮データベースファイルを使用したほうが、時間早いと思われる
if sample_f is not None:
    sample_df = pd.read_csv(sample_f,encoding ='CP932')
    sample = sample_df.iloc[:,sample_columns]#DPU用 sample_columns 2 or 5

    sample_1 = sample.to_list()#DPU用 sample_columns 2 or 5
    sample_1 = [str(x) for x in sample]
    sample_2 = [x for x in sample_1 if x != "nan"]

    sample_par = sample_2
    #sample_par = [x.strip() for x in sample_par]
    #sample_par = [str(x) for x in sample_par]

    if sample_columns == 5: #WEC
        initial_x_value = "NE"
        initial_y_value = "P_Manifold1"
    else:
        initial_x_value = "nmot"
        initial_y_value = "rl"

    if initial_x_value in sample_par and initial_y_value in sample_par:
        initial_x_index = sample_par.index(initial_x_value)
        initial_y_index = sample_par.index(initial_y_value)

    else:
        initial_x_index = 0  # 初期値が見つからない場合は最初の項目を選択
        initial_y_index = 0  # 初期値が見つからない場合は最初の項目を選択

    with st.sidebar:
        x_pal = st.selectbox('x列を選択してください', sample_par, index=initial_x_index)


        #ここでデータを読んで上下限を設定したい
        if x_pal == "NE" or x_pal == "nmot": 
            max_x_value = 8000
        else:
            max_x_value = 100
        x_lower_bound = st.number_input('xの下限値と',step=1)
        x_upper_bound = st.number_input('xの上限値を入力してください', value = max_x_value , step=10) 
        
        y_pal=st.selectbox('y列を選択してください', sample_par , index=initial_y_index )
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
    subplot_titles=("時間頻度", "Scatter Plot"),
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

    #分割数　10として　3Dマップを作る
            x_span = (x_upper_bound - x_lower_bound)/x_div_num
            y_span = (y_upper_bound - y_lower_bound)/y_div_num    
            
            for xx in range(x_div_num):
                x = xx * x_span + int(x_lower_bound)
                z_sum[x] = {}    
                for yy in range(y_div_num):
                    y = yy * y_span + int(y_lower_bound)
                    # NumPyを使用してフィルタリング
                    mask_x = (df[x_pal] > x) & (df[x_pal] <= x + x_span)
                    mask_y = (df[y_pal] > y) & (df[y_pal] <= y + y_span)
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

    z_sum = sum(z_values)
    z_values_normalized = []
    for z in z_values:
        # zが0の場合を考慮して、ゼロ除算を防ぐ
        if z_sum != 0:
            z_values_normalized.append(z / z_sum *100)
        else:
            z_values_normalized.append(0)  # ゼロ除算の場合、無次元化された値も0に設定

# もう一つのデータ群の処理を追加
    # <--- 追加開始

    if uploaded_files2 is not None:
        for uploaded_file in uploaded_files2:
            initial_lines = pd.read_csv(uploaded_file, nrows=2)
            uploaded_file.seek(0)
            if initial_lines.apply(lambda x: x.astype(str).str.contains(specific_string).any(), axis=1).any():
                sample_columns = 2
                skiprows = 5
            else:
                sample_columns = 5
                skiprows = 0

            df = pd.read_csv(uploaded_file, sep="[\t\0]", skiprows=skiprows, engine="python")
            dataframes2[uploaded_file.name] = df

    total_counts2 = {}
    for filename, df in dataframes2.items():
        if df.empty:
            continue
        # 同様にZデータを集計
        z_sum2 = {}
        for xx in range(x_div_num):
            x = xx * x_span + int(x_lower_bound)
            z_sum2[x] = {}
            for yy in range(y_div_num):
                y = yy * y_span + int(y_lower_bound)
                mask_x = (df[x_pal] > x) & (df[x_pal] <= x + x_span)
                mask_y = (df[y_pal] > y) & (df[y_pal] <= y + y_span)
                filtered_data = df[mask_x & mask_y]
                z_sum2[x][y] = len(filtered_data)
        
        for x in z_sum2:
            if x not in total_counts2:
                total_counts2[x] = {}
            for y in z_sum2[x]:
                total_counts2[x][y] = total_counts2.get(x, {}).get(y, 0) + z_sum2[x][y]

    # Zデータの有意差検証
    # <--- 追加終了
    z_values2 = []
    for x in total_counts2:
        for y in total_counts2[x]:
            z_values2.append(total_counts2[x][y])

    # t検定
    if len(z_values) > 0 and len(z_values2) > 0:
        t_stat, p_value = stats.ttest_ind(z_values, z_values2)
        st.write(f"t-statistic: {t_stat}, p-value: {p_value}")

        # Streamlitのセッションステートで表示データの管理
    if 'show_normalized' not in st.session_state:
        st.session_state.show_normalized = True  # 初期値として無次元化データを表示


# ボタンを横に並べるためのカラムを作成
    col3, col4 = st.columns([1,3])#幅を　1:3

    # 無次元化データを切り替えるボタン
    # グラフ表示ボタン
    with col3:
        if st.button('グラフを表示/非表示'):
            st.session_state.show_graph = not st.session_state.show_graph
            
    with col4:
        if st.button('時間　⇔　％　切り替え'):
            st.session_state.show_normalized = not st.session_state.show_normalized

    # 3Dグラフに表示するz_valuesを選択
    if st.session_state.show_normalized:
        z_to_use = z_values_normalized
        z_label = "時間頻度(%)"
    else:
        z_to_use = z_values
        z_label = "時間(sec)"


    for i in range(len(x_values)):
        fig.add_trace(go.Scatter3d(
            x=[x_values[i]+x_span/100, x_values[i]+x_span/100,x_values[i]+x_span/100, x_values[i]+x_span/100, x_values[i]+x_span/100],
            y=[y_values[i]-y_span/100, y_values[i]-y_span/100, y_values[i]-y_span/100, y_values[i]-y_span/100, y_values[i]-y_span/100],
            z=[0, z_to_use[i] ,z_to_use[i] ,0, 0],
            mode='lines',
            line=dict(width=10,color = 'rgba(0, 0, 0, 0.3)'),
            showlegend = False
            ),
            row=1,
            col=1)    

    for i in range(len(x_values)):
        fig.add_trace(go.Scatter3d(
            x=[x_values[i], x_values[i], x_values[i], x_values[i], x_values[i]],
            y=[y_values[i], y_values[i], y_values[i], y_values[i], y_values[i]],
            z=[0, z_to_use[i] , z_to_use[i] ,0, 0],
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
        title = "全 {:.3f} Hr ({} sec)".format(sumall,int(sumall*3600)),
        scene = dict(
        xaxis_title= x_pal,
        yaxis_title= y_pal,
        zaxis_title= z_label,
        xaxis=dict(range=[x_lower_bound,x_upper_bound]),  # X 軸の上下限
        yaxis=dict(range=[y_lower_bound,y_upper_bound]),
        camera=dict(eye=dict(x=1.25, y=-1.25, z=1.25))  # Y 軸の上下限
           # Z 軸の上下限
        ),
        scene2 = dict(
        xaxis_title= x_pal,
        yaxis_title= y_pal,
        xaxis=dict(range=[x_lower_bound,x_upper_bound]),  # X 軸の上下限
        yaxis=dict(range=[y_lower_bound,y_upper_bound])
        ),
        height = 600 ,
        width = 1600 ,
    )
    # 2D グラフのタイトルと軸ラベルを設定
    fig.update_xaxes(title_text=x_pal, range=[x_lower_bound,x_upper_bound], row=1, col=2)
    fig.update_yaxes(title_text=y_pal, range=[y_lower_bound,y_upper_bound], row=1, col=2)
    fig.update_layout(legend=dict(
    orientation="v",  # 水平に配置
    yanchor="top",
    y=1.0 ,  # グラの上側に配置
    xanchor="left",
    x=0.42
     ) , # 左よりに配置
    )

    # 凡例の設定: 左のグラフにのみ凡例を表示
    fig.update_layout(
        showlegend=True,
    )

    # 右側のグラフの凡例を非表示にする    
    if 'show_graph' not in st.session_state:
        st.session_state.show_graph = False

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
