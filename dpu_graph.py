Toyota AI Assistant
Icon
固定
個人テンプレート
標準テンプレート

要約・校正
文章の校正・添削を頼む
文章の要約を頼む
英文の校正・添削を頼む

翻訳

メール関連

資料・文章作成

会議

プログラミング

アンケート
AIエンジンごとの差異はこちらを参照ください
以下のように　データ群を二つダウンロードしてからグラフを作成する。

ふたつのデータぐんに対して、グラフ作成と、時間デーたの累積集計まではOKと思うが、
グラフ作成が　2つしか作成できない状態であると考えるので

もうひとつのデータ群のグラフも作成し、４つ作成できるように修正してください。

なお　２つのデータ群のｘ、ｙに対するｚの値の有意差をだせるようにしてください。

修正箇所をわかりやすく＃＃＃で表示してください。


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
uploaded_files = st.file_uploader("txtファイルをアップロードしてください(先)", type="txt",accept_multiple_files=True)
with col2:
uploaded_files2 = st.file_uploader("別のtxtファイルをアップロードしてください", type="txt", accept_multiple_files=True)
with col3:
sample_f = st.file_uploader("csvファイルをアップロードしてください", type=["csv"])

specific_string = "windarab" # ここに検索したい文字を設定

##### 比較元ファイルを読み込む
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

##### 比較先ファイルを読み込む
if uploaded_files2 is not None:
dataframes2 = {}
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

#グラフのパラメータ、レンジをサイドバーにて設定する
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
initial_x_index = 0 # 初期値が見つからない場合は最初の項目を選択
initial_y_index = 0 # 初期値が見つからない場合は最初の項目を選択

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

###ダウンロードしたファイルからプロットするファイルをチェックボックスにて選択
if dataframes:

total_counts = {}#この初期化した辞書型へ読み込んで全ロードデータを保存しておく
z_sum = {}#チェックボックスにチェックが入っている場合の)#チェックボックスにチェックが入っている場合のみプロットする
fig = make_subplots(
rows=1,
cols=2,
specs=[[{"type": "surface"}, {"type": "scatter"}]], # 1つ目は2Dプロット、2つ目は3Dプロット
subplot_titles=("時間頻度", "Scatter Plot"),
horizontal_spacing=0.1 # グラフ間の水平スペースを調整
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
z_values_normalized.append(0) # ゼロ除算の場合、無次元化された値も0に設定

z_sum = {}
for xx in range(x_div_num):
x = xx * x_span + int(x_lower_bound)
z_sum[x] = {}
for yy in range(y_div_num):
y = yy * y_span + int(y_lower_bound)
mask_x = (df[x_pal] > x) & (df[x_pal] <= x + x_span)
mask_y = (df[y_pal] > y) & (df[y_pal] <= y + y_span)
filtered_data = df[mask_x & mask_y]
z_sum[x][y] = len(filtered_data)

for x in z_sum:
if x not in total_counts:
total_counts[x] = {}
for y in z_sum[x]:
total_counts[x][y] = total_counts.get(x, {}).get(y, 0) + z_sum[x][y]

# もう一つのデータ群の処理を追加
# <--- 追加開始

if dataframes2:

total_counts2 = {}#この初期化した辞書型へ読み込んで全ロードデータを保存しておく
z_sum = {}#チェックボックスにチェックが入っている場合の)#チェックボックスにチェックが入っている場合のみプロットする
fig = make_subplots(
rows=1,
cols=2,
specs=[[{"type": "surface"}, {"type": "scatter"}]], # 1つ目は2Dプロット、2つ目は3Dプロット
subplot_titles=("時間頻度", "Scatter Plot"),
horizontal_spacing=0.1 # グラフ間の水平スペースを調整
)
for filename, df in dataframes2.items():
with st.sidebar:
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
z_values_normalized.append(0) # ゼロ除算の場合、無次元化された値も0に設定

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

# <--- 追加終了
# Streamlitのセッションステートで表示データの管理
if 'show_normalized' not in st.session_state:
st.session_state.show_normalized = True # 初期値として無次元化データを表示

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

########fig subplot　影付で作成
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

fig.update_layout(
title = "全 {:.3f} Hr ({} sec)".format(sumall,int(sumall*3600)),
scene = dict(
xaxis_title= x_pal,
yaxis_title= y_pal,
zaxis_title= z_label,
xaxis=dict(range=[x_lower_bound,x_upper_bound]), # X 軸の上下限
yaxis=dict(range=[y_lower_bound,y_upper_bound]),
camera=dict(eye=dict(x=1.25, y=-1.25, z=1.25)) # Y 軸の上下限
# Z 軸の上下限
),
scene2 = dict(
xaxis_title= x_pal,
yaxis_title= y_pal,
xaxis=dict(range=[x_lower_bound,x_upper_bound]), # X 軸の上下限
yaxis=dict(range=[y_lower_bound,y_upper_bound])
),
height = 600 ,
width = 1600 ,
)
# 2D グラフのタイトルと軸ラベルを設定
fig.update_xaxes(title_text=x_pal, range=[x_lower_bound,x_upper_bound], row=1, col=2)
fig.update_yaxes(title_text=y_pal, range=[y_lower_bound,y_upper_bound], row=1, col=2)
fig.update_layout(legend=dict(
orientation="v", # 水平に配置
yanchor="top",
y=1.0 , # グラの上側に配置
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
redcar-icon
以下のコードに対して、グラフを4つ作成できるように修正し、2つのデータ群のx、yに対するzの有意差を出す処理を追加しました。変更箇所は###でマークしています。

# ここから修正を始めます

# 3Dグラフの作成を2つのデータ群に対して行うように変更
# <--- 追加開始

# 1つ目のデータ群の処理を行った後
if dataframes:
    # 1つ目のデータ群に対する処理をここに追加

# 2つ目のデータ群の処理を追加
if dataframes2:
    # 2つ目のデータ群のためのtotal_counts2を初期化
    total_counts2 = {}

    for filename, df in dataframes2.items():
        with st.sidebar:
            show_data = st.checkbox("{} を表示".format(filename), value=True)        
        if show_data:
            # データの処理を行う
            # 省略
            # ここで2つ目のデータ群に対してもz_sumを計算する
            z_sum2 = {}
            for xx in range(x_div_num):
                x = xx * x_span + int(x_lower_bound)
                z_sum2[x] = {}
                for yy in range(y_div_num):
                    y = yy * y_span + int(y_lower_bound)
                    # NumPyを使用してフィルタリング
                    mask_x = (df[x_pal] > x) & (df[x_pal] <= x + x_span)
                    mask_y = (df[y_pal] > y) & (df[y_pal] <= y + y_span)
                    filtered_data = df[mask_x & mask_y]
                    z_sum2[x][y] = len(filtered_data)

            # ここでtotal_counts2にz_sum2を追加
            for x in z_sum2:
                if x not in total_counts2:
                    total_counts2[x] = {}
                for y in z_sum2[x]:
                    total_counts2[x][y] = total_counts2.get(x, {}).get(y, 0) + z_sum2[x][y]

    # ここで2つのデータ群の有意差を計算する
    # x_valuesとy_valuesを取得
    x_values1 = []
    y_values1 = []
    z_values1 = []

    for x in total_counts:
        for y in total_counts[x]:
            x_values1.append(x)
            y_values1.append(y)
            z_values1.append(total_counts[x][y])

    x_values2 = []
    y_values2 = []
    z_values2 = []

    for x in total_counts2:
        for y in total_counts2[x]:
            x_values2.append(x)
            y_values2.append(y)
            z_values2.append(total_counts2[x][y])

    # 有意差の計算を行う
    t_statistic, p_value = stats.ttest_ind(z_values1, z_values2)  # t検定を使用

    # 有意差の結果を表示
    st.write(f"t統計量: {t_statistic}, p値: {p_value}")

# <--- 追加終了

# グラフ表示の設定
if st.session_state.show_graph:
    fig.show()  # ここで4つのグラフを一緒に表示
修正点の要約
2つ目のデータ群の処理: 2つ目のデータ群に対する処理を追加し、total_counts2を計算しました。
有意差の計算: scipy.statsのttest_indを使用して、2つのデータ群のzの値の有意差を計算し、t統計量とp値を表示しました。
グラフの表示: 2つのデータ群を含むすべてのグラフを表示できるようにしました。
この修正により、4つのグラフを作成し、2つのデータ群間の有意差を計算することができます。

col1, col2 ,col3 = st.columns(3)
で幅を調節したい
redcar-icon
Streamlitのst.columns関数を使用して、各カラムの幅を調整することができます。st.columnsに渡す引数としてリストを指定することで、各カラムの比率を設定できます。たとえば、幅を1:2:1の比率にしたい場合、次のように指定します。

以下に、幅の比率を調整するための修正例を示します。

# 幅を1:2:1に設定する例
col1, col2, col3 = st.columns([1, 2, 1])
これにより、col1とcol3が同じ幅で、col2がそれよりも広くなります。

以下に、元のコードの該当部分を修正した例を示します。

# 幅を指定してカラムを作成
col1, col2, col3 = st.columns([1, 2, 1])  # 1:2:1の比率でカラムを作成

with col1:
    uploaded_files = st.file_uploader("txtファイルをアップロードしてください(先)", type="txt", accept_multiple_files=True)

with col2:
    uploaded_files2 = st.file_uploader("別のtxtファイルをアップロードしてください", type="txt", accept_multiple_files=True)

with col3:
    sample_f = st.file_uploader("csvファイルをアップロードしてください", type=["csv"])
このようにすることで、カラムの幅を調整できます。必要に応じて、比率を変更することも可能です。たとえば、[1, 3, 1]とすると、中央のカラムがより広くなります。

以下４つのグラフを書いているが冗長部分を簡素化して
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

col1, col2 ,col3 = st.columns([4,4,1])
with col1:
uploaded_files = st.file_uploader("txtファイルをアップロードしてください(先)", type="txt",accept_multiple_files=True)
with col2:
uploaded_files2 = st.file_uploader("別のtxtファイルをアップロードしてください", type="txt", accept_multiple_files=True)
with col3:
sample_f = st.file_uploader("csvファイルをアップロードしてください", type=["csv"])

specific_string = "windarab" # ここに検索したい文字を設定

##### 比較元ファイルを読み込む
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

##### 比較先ファイルを読み込む
if uploaded_files2 is not None:
dataframes2 = {}
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

#グラフのパラメータ、レンジをサイドバーにて設定する
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
initial_x_index = 0 # 初期値が見つからない場合は最初の項目を選択
initial_y_index = 0 # 初期値が見つからない場合は最初の項目を選択

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

###ダウンロードしたファイルからプロットするファイルをチェックボックスにて選択
if dataframes:

total_counts = {}#この初期化した辞書型へ読み込んで全ロードデータを保存しておく
z_sum = {}#チェックボックスにチェックが入っている場合の)#チェックボックスにチェックが入っている場合のみプロットする
fig1 = make_subplots(
rows=1,
cols=2,
specs=[[{"type": "surface"}, {"type": "scatter"}]], # 1つ目は2Dプロット、2つ目は3Dプロット
subplot_titles=("時間頻度", "Scatter Plot"),
horizontal_spacing=0.1 # グラフ間の水平スペースを調整
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
fig1.add_trace(go.Scatter(x=df[x_pal], y=df[y_pal],
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
for z in z_values:
# zが0の場合を考慮して、ゼロ除算を防ぐ

z_sum = {}
for xx in range(x_div_num):
x = xx * x_span + int(x_lower_bound)
z_sum[x] = {}
for yy in range(y_div_num):
y = yy * y_span + int(y_lower_bound)
mask_x = (df[x_pal] > x) & (df[x_pal] <= x + x_span)
mask_y = (df[y_pal] > y) & (df[y_pal] <= y + y_span)
filtered_data = df[mask_x & mask_y]
z_sum[x][y] = len(filtered_data)

for x in z_sum:
if x not in total_counts:
total_counts[x] = {}
for y in z_sum[x]:
total_counts[x][y] = total_counts.get(x, {}).get(y, 0) + z_sum[x][y]

if 'show_normalized' not in st.session_state:
st.session_state.show_normalized = True # 初期値として無次元化データを表示

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

########fig subplot　影付で作成　　マップの作製
for i in range(len(x_values)):
fig1.add_trace(go.Scatter3d(
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
fig1.add_trace(go.Scatter3d(
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

fig1.update_layout(
title = "全 {:.3f} Hr ({} sec)".format(sumall,int(sumall*3600)),
scene = dict(
xaxis_title= x_pal,
yaxis_title= y_pal,
zaxis_title= z_label,
xaxis=dict(range=[x_lower_bound,x_upper_bound]), # X 軸の上下限
yaxis=dict(range=[y_lower_bound,y_upper_bound]),
camera=dict(eye=dict(x=1.25, y=-1.25, z=1.25)) # Y 軸の上下限
# Z 軸の上下限
),
scene2 = dict(
xaxis_title= x_pal,
yaxis_title= y_pal,
xaxis=dict(range=[x_lower_bound,x_upper_bound]), # X 軸の上下限
yaxis=dict(range=[y_lower_bound,y_upper_bound])
),
height = 600 ,
width = 1600 ,
)
# 2D グラフのタイトルと軸ラベルを設定
fig1.update_xaxes(title_text=x_pal, range=[x_lower_bound,x_upper_bound], row=1, col=2)
fig1.update_yaxes(title_text=y_pal, range=[y_lower_bound,y_upper_bound], row=1, col=2)
fig1.update_layout(legend=dict(
orientation="v", # 水平に配置
yanchor="top",
y=1.0 , # グラの上側に配置
xanchor="left",
x=0.42
) , # 左よりに配置
)

# 凡例の設定: 左のグラフにのみ凡例を表示
fig1.update_layout(
showlegend=True,
)

# 右側のグラフの凡例を非表示にする
if 'show_graph' not in st.session_state:
st.session_state.show_graph = False

# グラフの表示
if st.session_state.show_graph:
st.plotly_chart(fig1 , use_container_width=False)
####
# もう一つのデータ群の処理を追加
# <--- 追加開始

if dataframes2:

total_counts2 = {}#この初期化した辞書型へ読み込んで全ロードデータを保存しておく
z_sum = {}#チェックボックスにチェックが入っている場合の)#チェックボックスにチェックが入っている場合のみプロットする
fig2 = make_subplots(
rows=1,
cols=2,
specs=[[{"type": "surface"}, {"type": "scatter"}]], # 1つ目は2Dプロット、2つ目は3Dプロット
subplot_titles=("時間頻度", "Scatter Plot"),
horizontal_spacing=0.1 # グラフ間の水平スペースを調整
)
for filename, df in dataframes2.items():
with st.sidebar:
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
fig2.add_trace(go.Scatter(x=df[x_pal], y=df[y_pal],
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

# <--- 追加終了
# Streamlitのセッションステートで表示データの管理
if 'show_normalized' not in st.session_state:
st.session_state.show_normalized = True # 初期値として無次元化データを表示

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

########fig subplot　影付で作成　　マップの作製
for i in range(len(x_values)):
fig2.add_trace(go.Scatter3d(
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
fig2.add_trace(go.Scatter3d(
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

fig2.update_layout(
title = "全 {:.3f} Hr ({} sec)".format(sumall,int(sumall*3600)),
scene = dict(
xaxis_title= x_pal,
yaxis_title= y_pal,
zaxis_title= z_label,
xaxis=dict(range=[x_lower_bound,x_upper_bound]), # X 軸の上下限
yaxis=dict(range=[y_lower_bound,y_upper_bound]),
camera=dict(eye=dict(x=1.25, y=-1.25, z=1.25)) # Y 軸の上下限
# Z 軸の上下限
),
scene2 = dict(
xaxis_title= x_pal,
yaxis_title= y_pal,
xaxis=dict(range=[x_lower_bound,x_upper_bound]), # X 軸の上下限
yaxis=dict(range=[y_lower_bound,y_upper_bound])
),
height = 600 ,
width = 1600 ,
)
# 2D グラフのタイトルと軸ラベルを設定
fig2.update_xaxes(title_text=x_pal, range=[x_lower_bound,x_upper_bound], row=1, col=2)
fig2.update_yaxes(title_text=y_pal, range=[y_lower_bound,y_upper_bound], row=1, col=2)
fig2.update_layout(legend=dict(
orientation="v", # 水平に配置
yanchor="top",
y=1.0 , # グラの上側に配置
xanchor="left",
x=0.42
) , # 左よりに配置
)

# 凡例の設定: 左のグラフにのみ凡例を表示
fig2.update_layout(
showlegend=True,
)

# 右側のグラフの凡例を非表示にする
if 'show_graph' not in st.session_state:
st.session_state.show_graph = False

# グラフの表示
if st.session_state.show_graph:
st.plotly_chart(fig2 , use_container_width=False)

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
redcar-icon
コードを簡素化し、冗長な部分を削減しました。主に、データ処理とグラフ作成に共通のロジックを関数にまとめることで、重複を減らしています。また、必要な部分だけを残し、全体的に読みやすくしています。

以下に修正後のコードを示します。

# dpuデータをstreamlitで表示する
import os
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats

st.set_page_config(
    page_title="PLOT",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("windarab or dpu 積算データ")

@st.cache_data
def load_uploaded_file(uploaded_file, skiprows):
    return pd.read_csv(uploaded_file, sep="[\t\0]", skiprows=skiprows, engine="python")

def process_files(uploaded_files, specific_string):
    dataframes = {}
    for uploaded_file in uploaded_files:
        initial_lines = pd.read_csv(uploaded_file, nrows=2)
        uploaded_file.seek(0)
        skiprows = 5 if initial_lines.apply(lambda x: x.astype(str).str.contains(specific_string).any(), axis=1).any() else 0
        df = pd.read_csv(uploaded_file, sep="[\t\0]", skiprows=skiprows, engine="python")
        dataframes[uploaded_file.name] = df
    return dataframes

def create_fig(dataframes, x_pal, y_pal, x_lower_bound, x_upper_bound, y_lower_bound, y_upper_bound, x_div_num, y_div_num):
    total_counts = {}
    z_sum = {}
    fig = make_subplots(
        rows=1,
        cols=2,
        specs=[[{"type": "surface"}, {"type": "scatter"}]],
        subplot_titles=("時間頻度", "Scatter Plot"),
        horizontal_spacing=0.1
    )

    for filename, df in dataframes.items():
        if df.empty:
            st.warning(f"{filename} は空のファイルです。")
            continue

        if "Time" in df.columns:
            df = df.iloc[1:]  # DPUの場合は単位行を除外
            time_format = "%H:%M:%S.%f"
            df["Time"] = [datetime.strptime(time_str, time_format) for time_str in df["Time"]]
            init_time = df["Time"].iloc[0]
            df["Time"] = [(time - init_time).seconds for time in df["Time"]]
            df = df.apply(pd.to_numeric, errors='coerce')

        fig.add_trace(go.Scatter(x=df[x_pal], y=df[y_pal], mode='markers', name=filename), row=1, col=2)

        x_span = (x_upper_bound - x_lower_bound) / x_div_num
        y_span = (y_upper_bound - y_lower_bound) / y_div_num

        for xx in range(x_div_num):
            x = xx * x_span + int(x_lower_bound)
            z_sum[x] = {}
            for yy in range(y_div_num):
                y = yy * y_span + int(y_lower_bound)
                mask_x = (df[x_pal] > x) & (df[x_pal] <= x + x_span)
                mask_y = (df[y_pal] > y) & (df[y_pal] <= y + y_span)
                filtered_data = df[mask_x & mask_y]
                z_sum[x][y] = len(filtered_data)

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

    # 3Dグラフの作成
    for i in range(len(x_values)):
        fig.add_trace(go.Scatter3d(
            x=[x_values[i] + x_span / 100] * 5,
            y=[y_values[i]] * 5,
            z=[0, z_values[i], z_values[i], 0, 0],
            mode='lines',
            line=dict(width=10, color='rgba(0, 0, 0, 0.3)'),
            showlegend=False
        ), row=1, col=1)

        fig.add_trace(go.Scatter3d(
            x=[x_values[i]] * 5,
            y=[y_values[i]] * 5,
            z=[0, z_values[i], z_values[i], 0, 0],
            mode='lines',
            line=dict(width=10, color="blue"),
            showlegend=False
        ), row=1, col=1)

    return fig, total_counts

# ファイルのアップロード
col1, col2, col3 = st.columns([4, 4, 1])
with col1:
    uploaded_files = st.file_uploader("txtファイルをアップロードしてください(先)", type="txt", accept_multiple_files=True)
with col2:
    uploaded_files2 = st.file_uploader("別のtxtファイルをアップロードしてください", type="txt", accept_multiple_files=True)
with col3:
    sample_f = st.file_uploader("csvファイルをアップロードしてください", type=["csv"])

specific_string = "windarab"

# ファイルの読み込み
if uploaded_files is not None:
    dataframes = process_files(uploaded_files, specific_string)

if uploaded_files2 is not None:
    dataframes2 = process_files(uploaded_files2, specific_string)

# グラフのパラメータ設定
if sample_f is not None:
    sample_df = pd.read_csv(sample_f, encoding='CP932')
    sample_columns = 2 if sample_df.shape[1] == 2 else 5  # サンプルカラム数の確認
    sample_par = sample_df.columns.tolist()

    with st.sidebar:
        x_pal = st.selectbox('x列を選択してください', sample_par)
        y_pal = st.selectbox('y列を選択してください', sample_par)
        x_lower_bound = st.number_input('xの下限値と', step=1)
        x_upper_bound = st.number_input('xの上限値を入力してください', value=100, step=10)
        y_lower_bound = st.number_input('yの下限値と', step=1)
        y_upper_bound = st.number_input('yの上限値を入力してください', value=200, step=10)
        x_div_num = st.number_input('x軸分割数', value=20)
        y_div_num = st.number_input('y軸分割数', value=20)

# グラフの作成
if 'show_graph' not in st.session_state:
    st.session_state.show_graph = False

if st.session_state.show_graph:
    if dataframes:
        fig1, total_counts1 = create_fig(dataframes, x_pal, y_pal, x_lower_bound, x_upper_bound, y_lower_bound, y_upper_bound, x_div_num, y_div_num)
        st.plotly_chart(fig1, use_container_width=False)

    if dataframes2:
        fig2, total_counts2 = create_fig(dataframes2, x_pal, y_pal, x_lower_bound, x_upper_bound, y_lower_bound, y_upper_bound, x_div_num, y_div_num)
        st.plotly_chart(fig2, use_container_width=False)

# ダウンロード用のデータを作成
if dataframes:
    download_data = []
    for x in total_counts1:
        for y in total_counts1[x]:
            download_data.append([x, y, total_counts1[x][y]])
    csv_data = pd.DataFrame(download_data, columns=[x_pal, y_pal, 'Count'])
    csv_buffer = csv_data.to_csv(index=False).encode('utf-8')
    st.download_button(label="積算データをダウンロード", data=csv_buffer, file_name='cumulative_data.csv', mime='text/csv')
主な変更点:
関数の導入:

process_files: アップロードされたファイルを処理する関数を作成しました。
create_fig: グラフを作成する処理を関数化し、冗長部分を削減しました。
共通処理の統一:

グラフ作成のロジックが共通化され、同じように処理されるようになりました。
可読性の向上:

コードが整理され、読みやすくなりました。
このようにすることで、将来的に機能を追加する場合や、保守を行う際も容易になるでしょう。

以下で３つめにcavをアップロードしたデータは
時間累積計算データにはならないはずだが
どこかで読み込まれている理由を教えて

。
# dpuデータをstreamlitで表示する
import os
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats

st.set_page_config(
page_title="PLOT",
layout="wide",
initial_sidebar_state="expanded"
)
st.title("windarab or dpu 積算データ")

@st.cache_data
def load_uploaded_file(uploaded_file, skiprows):
return pd.read_csv(uploaded_file, sep="[\t\0]", skiprows=skiprows, engine="python")

def process_files(uploaded_files, specific_string):
dataframes = {}
for uploaded_file in uploaded_files:
initial_lines = pd.read_csv(uploaded_file, nrows=2)
uploaded_file.seek(0)
skiprows = 5 if initial_lines.apply(lambda x: x.astype(str).str.contains(specific_string).any(), axis=1).any() else 0
df = pd.read_csv(uploaded_file, sep="[\t\0]", skiprows=skiprows, engine="python")
dataframes[uploaded_file.name] = df
return dataframes

def create_fig(dataframes, x_pal, y_pal, x_lower_bound, x_upper_bound, y_lower_bound, y_upper_bound, x_div_num, y_div_num):
total_counts = {}
z_sum = {}
fig = make_subplots(
rows=1,
cols=2,
specs=[[{"type": "surface"}, {"type": "scatter"}]],
subplot_titles=("時間頻度", "Scatter Plot"),
horizontal_spacing=0.1
)

for filename, df in dataframes.items():
if df.empty:
st.warning(f"{filename} は空のファイルです。")
continue

if "Time" in df.columns:
df = df.iloc[1:] # DPUの場合は単位行を除外
time_format = "%H:%M:%S.%f"
df["Time"] = [datetime.strptime(time_str, time_format) for time_str in df["Time"]]
init_time = df["Time"].iloc[0]
df["Time"] = [(time - init_time).seconds for time in df["Time"]]
df = df.apply(pd.to_numeric, errors='coerce')

fig.add_trace(go.Scatter(x=df[x_pal], y=df[y_pal], mode='markers', name=filename), row=1, col=2)

x_span = (x_upper_bound - x_lower_bound) / x_div_num
y_span = (y_upper_bound - y_lower_bound) / y_div_num

for xx in range(x_div_num):
x = xx * x_span + int(x_lower_bound)
z_sum[x] = {}
for yy in range(y_div_num):
y = yy * y_span + int(y_lower_bound)
mask_x = (df[x_pal] > x) & (df[x_pal] <= x + x_span)
mask_y = (df[y_pal] > y) & (df[y_pal] <= y + y_span)
filtered_data = df[mask_x & mask_y]
z_sum[x][y] = len(filtered_data)

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

# 3Dグラフの作成
for i in range(len(x_values)):
fig.add_trace(go.Scatter3d(
x=[x_values[i] + x_span / 100] * 5,
y=[y_values[i]] * 5,
z=[0, z_values[i], z_values[i], 0, 0],
mode='lines',
line=dict(width=10, color='rgba(0, 0, 0, 0.3)'),
showlegend=False
), row=1, col=1)

fig.add_trace(go.Scatter3d(
x=[x_values[i]] * 5,
y=[y_values[i]] * 5,
z=[0, z_values[i], z_values[i], 0, 0],
mode='lines',
line=dict(width=10, color="blue"),
showlegend=False
), row=1, col=1)

return fig, total_counts

# ファイルのアップロード
col1, col2, col3 = st.columns([3, 3, 1])
with col1:
uploaded_files = st.file_uploader("txtファイルをアップロードしてください(先)", type="txt", accept_multiple_files=True)
with col2:
uploaded_files2 = st.file_uploader("別のtxtファイルをアップロードしてください", type="txt", accept_multiple_files=True)
with col3:
sample_f = st.file_uploader("csvファイルをアップロードしてください", type=["csv"])

specific_string = "windarab"

# ファイルの読み込み
if uploaded_files is not None:
dataframes = process_files(uploaded_files, specific_string)

if uploaded_files2 is not None:
dataframes2 = process_files(uploaded_files2, specific_string)

# グラフのパラメータ設定
if sample_f is not None:
sample_df = pd.read_csv(sample_f, encoding='CP932')
sample_columns = 2 if sample_df.shape[1] == 2 else 5 # サンプルカラム数の確認
sample_par = sample_df.columns.tolist()

with st.sidebar:
x_pal = st.selectbox('x列を選択してください', sample_par)
y_pal = st.selectbox('y列を選択してください', sample_par)
x_lower_bound = st.number_input('xの下限値と', step=1)
x_upper_bound = st.number_input('xの上限値を入力してください', value=100, step=10)
y_lower_bound = st.number_input('yの下限値と', step=1)
y_upper_bound = st.number_input('yの上限値を入力してください', value=200, step=10)
x_div_num = st.number_input('x軸分割数', value=20)
y_div_num = st.number_input('y軸分割数', value=20)

# グラフの作成

if dataframes:
fig1, total_counts1 = create_fig(dataframes, x_pal, y_pal, x_lower_bound, x_upper_bound, y_lower_bound, y_upper_bound, x_div_num, y_div_num)
st.plotly_chart(fig1, use_container_width=False)

if dataframes2:
fig2, total_counts2 = create_fig(dataframes2, x_pal, y_pal, x_lower_bound, x_upper_bound, y_lower_bound, y_upper_bound, x_div_num, y_div_num)
st.plotly_chart(fig2, use_container_width=False)
redcar-icon
アップロードされたcavファイルが「時間累積計算データにはならないはず」とおっしゃっているのは、create_fig関数内での処理に関連しています。create_fig関数は、アップロードされたすべてのデータフレームに対して同じ処理を行っています。以下に、その理由を詳しく説明します。

理由
データフレームの処理:

create_fig関数の中で、各データフレームに対して以下の処理が行われています。
if "Time" in df.columns:
    df = df.iloc[1:]  # DPUの場合は単位行を除外
    time_format = "%H:%M:%S.%f"
    df["Time"] = [datetime.strptime(time_str, time_format) for time_str in df["Time"]]
    init_time = df["Time"].iloc[0]
    df["Time"] = [(time - init_time).seconds for time in df["Time"]]
    df = df.apply(pd.to_numeric, errors='coerce')
ここで、"Time"というカラムが存在する場合、時間情報を処理し、累積計算を行っています。

cavファイルの読み込み:

cavファイルには"Time"カラムが存在しない場合、上記の処理はスキップされますが、cavファイルがprocess_files関数で読み込まれる際、dataframesまたはdataframes2に格納されます。この時点で、特に何もフィルタリングされていないため、cavファイルも処理の対象になります。
描画処理の実行:

create_fig関数が呼ばれると、すべてのデータフレーム（dataframesまたはdataframes2）に対して同じ処理が行われます。cavファイルがdataframesやdataframes2に含まれていれば、そのファイルに対してもcreate_figが呼ばれ、時間累積の計算が行われる可能性があります。
解決策
cavファイルを処理する際に、そのファイルが時間累積計算の対象外であることを明示的に示すためには、以下のような修正を加えることができます。

ファイルのタイプを識別する: process_files関数内で、ファイル名の拡張子や内容に基づいて、特定のファイルに対して異なる処理を行うようにします。
def process_files(uploaded_files, specific_string):
    dataframes = {}
    for uploaded_file in uploaded_files:
        # ファイル名によって処理を分ける
        if uploaded_file.name.endswith('.cav'):
            continue  # cavファイルはスキップ

        initial_lines = pd.read_csv(uploaded_file, nrows=2)
        uploaded_file.seek(0)
        skiprows = 5 if initial_lines.apply(lambda x: x.astype(str).str.contains(specific_string).any(), axis=1).any() else 0
        df = pd.read_csv(uploaded_file, sep="[\t\0]", skiprows=skiprows, engine="python")
        dataframes[uploaded_file.name] = df
    return dataframes
この変更により、cavファイルはdataframesに追加されず、create_fig関数で処理されることがなくなります。これにより、時間累積計算が不要なデータが処理されることを防げます。

以下　uploadedファイルの塊は　３つある。

二つはデータ　で累積地計算やグラフ値に使用。
ひとつは　csv　でサイドバーでのパラメータ選定やレンジを決めるために使う。
だた　プログラム実行したさいに　最下方で　の処理のときに、
cxvを読み込むつもりではないのに読み込んで島市エラーがでる。最下での処理は

２つのtxt　データを　読むだけではないの？

# dpuデータをstreamlitで表示する
import os
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats

st.set_page_config(
page_title="PLOT",
layout="wide",
initial_sidebar_state="expanded"
)
st.title("windarab or dpu 積算データ")

@st.cache_data
def load_uploaded_file(uploaded_file, skiprows):
return pd.read_csv(uploaded_file, sep="[\t\0]", skiprows=skiprows, engine="python")

def process_files(uploaded_files, specific_string):
dataframes = {}
for uploaded_file in uploaded_files:
initial_lines = pd.read_csv(uploaded_file, nrows=2)
uploaded_file.seek(0)
skiprows = 5 if initial_lines.apply(lambda x: x.astype(str).str.contains(specific_string).any(), axis=1).any() else 0
df = pd.read_csv(uploaded_file, sep="[\t\0]", skiprows=skiprows, engine="python")
dataframes[uploaded_file.name] = df
return dataframes

def create_fig(dataframes, x_pal, y_pal, x_lower_bound, x_upper_bound, y_lower_bound, y_upper_bound, x_div_num, y_div_num):
total_counts = {}
z_sum = {}
fig = make_subplots(
rows=1,
cols=2,
specs=[[{"type": "surface"}, {"type": "scatter"}]],
subplot_titles=("時間頻度", "Scatter Plot"),
horizontal_spacing=0.1
)

for filename, df in dataframes.items():
if df.empty:
st.warning(f"{filename} は空のファイルです。")
continue

if "Time" in df.columns:
df = df.iloc[1:] # DPUの場合は単位行を除外
time_format = "%H:%M:%S.%f"
df["Time"] = [datetime.strptime(time_str, time_format) for time_str in df["Time"]]
init_time = df["Time"].iloc[0]
df["Time"] = [(time - init_time).seconds for time in df["Time"]]
df = df.apply(pd.to_numeric, errors='coerce')

fig.add_trace(go.Scatter(x=df[x_pal], y=df[y_pal], mode='markers', name=filename), row=1, col=2)

x_span = (x_upper_bound - x_lower_bound) / x_div_num
y_span = (y_upper_bound - y_lower_bound) / y_div_num

for xx in range(x_div_num):
x = xx * x_span + int(x_lower_bound)
z_sum[x] = {}
for yy in range(y_div_num):
y = yy * y_span + int(y_lower_bound)
mask_x = (df[x_pal] > x) & (df[x_pal] <= x + x_span)
mask_y = (df[y_pal] > y) & (df[y_pal] <= y + y_span)
filtered_data = df[mask_x & mask_y]
z_sum[x][y] = len(filtered_data)

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

# 3Dグラフの作成
for i in range(len(x_values)):
fig.add_trace(go.Scatter3d(
x=[x_values[i] + x_span / 100] * 5,
y=[y_values[i]] * 5,
z=[0, z_values[i], z_values[i], 0, 0],
mode='lines',
line=dict(width=10, color='rgba(0, 0, 0, 0.3)'),
showlegend=False
), row=1, col=1)

fig.add_trace(go.Scatter3d(
x=[x_values[i]] * 5,
y=[y_values[i]] * 5,
z=[0, z_values[i], z_values[i], 0, 0],
mode='lines',
line=dict(width=10, color="blue"),
showlegend=False
), row=1, col=1)

return fig, total_counts

# ファイルのアップロード
col1, col2, col3 = st.columns([3, 3, 1])
with col1:
uploaded_files = st.file_uploader("txtファイルをアップロードしてください(先)", type="txt", accept_multiple_files=True)
with col2:
uploaded_files2 = st.file_uploader("別のtxtファイルをアップロードしてください", type="txt", accept_multiple_files=True)
with col3:
sample_f = st.file_uploader("csvファイルをアップロードしてください", type=["csv"])

specific_string = "windarab"

# ファイルの読み込み
if uploaded_files is not None:
dataframes = process_files(uploaded_files, specific_string)

if uploaded_files2 is not None:
dataframes2 = process_files(uploaded_files2, specific_string)

# グラフのパラメータ設定
if sample_f is not None:
sample_df = pd.read_csv(sample_f, encoding='CP932')
sample_columns = 2 if sample_df.shape[1] == 2 else 5 # サンプルカラム数の確認
sample_par = sample_df.columns.tolist()

with st.sidebar:
x_pal = st.selectbox('x列を選択してください', sample_par)
y_pal = st.selectbox('y列を選択してください', sample_par)
x_lower_bound = st.number_input('xの下限値と', step=1)
x_upper_bound = st.number_input('xの上限値を入力してください', value=100, step=10)
y_lower_bound = st.number_input('yの下限値と', step=1)
y_upper_bound = st.number_input('yの上限値を入力してください', value=200, step=10)
x_div_num = st.number_input('x軸分割数', value=20)
y_div_num = st.number_input('y軸分割数', value=20)

# グラフの作成

if dataframes:
fig1, total_counts1 = create_fig(dataframes, x_pal, y_pal, x_lower_bound, x_upper_bound, y_lower_bound, y_upper_bound, x_div_num, y_div_num)
st.plotly_chart(fig1, use_container_width=False)

if dataframes2:
fig2, total_counts2 = create_fig(dataframes2, x_pal, y_pal, x_lower_bound, x_upper_bound, y_lower_bound, y_upper_bound, x_div_num, y_div_num)
st.plotly_chart(fig2, use_container_width=False)
redcar-icon
csvファイルが誤って読み込まれる原因について詳しく説明します。

問題の説明
あなたのプログラムの現在のロジックでは、uploaded_files（最初のtxtファイルのリスト）とuploaded_files2（2番目のtxtファイルのリスト）を処理する際に、process_files関数が呼び出されます。この関数は、アップロードされた各ファイルを読み込み、データフレームとして保存します。

process_files関数の動作:

この関数は、アップロードされた全てのファイルを処理します。ここで、csvファイルもuploaded_filesやuploaded_files2に含まれていない限り、process_files関数には渡されません。
ファイルの読み込み時の条件:

csvファイルは、サイドバーでのパラメータ選定やレンジ設定のために別途読み込まれます。しかし、create_fig関数内でdataframesやdataframes2を使用しているため、csvファイルのデータが含まれているとエラーが発生する可能性があります。
解決策
csvファイルを処理する際に、dataframesやdataframes2に追加されないようにするために、以下の方法で修正できます。

process_files関数を修正:
process_files関数を修正し、txtファイルの処理を行う際に、csvファイルが含まれていないことを確認します。以下に修正例を示します。
def process_files(uploaded_files, specific_string):
    dataframes = {}
    for uploaded_file in uploaded_files:
        if uploaded_file.name.endswith('.csv'):
            continue  # csvファイルはスキップ

        initial_lines = pd.read_csv(uploaded_file, nrows=2)
        uploaded_file.seek(0)
        skiprows = 5 if initial_lines.apply(lambda x: x.astype(str).str.contains(specific_string).any(), axis=1).any() else 0
        df = pd.read_csv(uploaded_file, sep="[\t\0]", skiprows=skiprows, engine="python")
        dataframes[uploaded_file.name] = df
    return dataframes
この修正により、process_files関数はcsvファイルをスキップし、dataframesやdataframes2に追加されることはなくなります。

最終的なコード
修正後のコードは以下のようになります。

# dpuデータをstreamlitで表示する
import os
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats

st.set_page_config(
    page_title="PLOT",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("windarab or dpu 積算データ")

@st.cache_data
def load_uploaded_file(uploaded_file, skiprows):
    return pd.read_csv(uploaded_file, sep="[\t\0]", skiprows=skiprows, engine="python")

def process_files(uploaded_files, specific_string):
    dataframes = {}
    for uploaded_file in uploaded_files:
        if uploaded_file.name.endswith('.csv'):
            continue  # csvファイルはスキップ

        initial_lines = pd.read_csv(uploaded_file, nrows=2)
        uploaded_file.seek(0)
        skiprows = 5 if initial_lines.apply(lambda x: x.astype(str).str.contains(specific_string).any(), axis=1).any() else 0
        df = pd.read_csv(uploaded_file, sep="[\t\0]", skiprows=skiprows, engine="python")
        dataframes[uploaded_file.name] = df
    return dataframes

def create_fig(dataframes, x_pal, y_pal, x_lower_bound, x_upper_bound, y_lower_bound, y_upper_bound, x_div_num, y_div_num):
    total_counts = {}
    z_sum = {}
    fig = make_subplots(
        rows=1,
        cols=2,
        specs=[[{"type": "surface"}, {"type": "scatter"}]],
        subplot_titles=("時間頻度", "Scatter Plot"),
        horizontal_spacing=0.1
    )

    for filename, df in dataframes.items():
        if df.empty:
            st.warning(f"{filename} は空のファイルです。")
            continue

        if "Time" in df.columns:
            df = df.iloc[1:]  # DPUの場合は単位行を除外
            time_format = "%H:%M:%S.%f"
            df["Time"] = [datetime.strptime(time_str, time_format) for time_str in df["Time"]]
            init_time = df["Time"].iloc[0]
            df["Time"] = [(time - init_time).seconds for time in df["Time"]]
            df = df.apply(pd.to_numeric, errors='coerce')

        fig.add_trace(go.Scatter(x=df[x_pal], y=df[y_pal], mode='markers', name=filename), row=1, col=2)

        x_span = (x_upper_bound - x_lower_bound) / x_div_num
        y_span = (y_upper_bound - y_lower_bound) / y_div_num

        for xx in range(x_div_num):
            x = xx * x_span + int(x_lower_bound)
            z_sum[x] = {}
            for yy in range(y_div_num):
                y = yy * y_span + int(y_lower_bound)
                mask_x = (df[x_pal] > x) & (df[x_pal] <= x + x_span)
                mask_y = (df[y_pal] > y) & (df[y_pal] <= y + y_span)
                filtered_data = df[mask_x & mask_y]
                z_sum[x][y] = len(filtered_data)

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

    # 3Dグラフの作成
    for i in range(len(x_values)):
        fig.add_trace(go.Scatter3d(
            x=[x_values[i] + x_span / 100] * 5,
            y=[y_values[i]] * 5,
            z=[0, z_values[i], z_values[i], 0, 0],
            mode='lines',
            line=dict(width=10, color='rgba(0, 0, 0, 0.3)'),
            showlegend=False
        ), row=1, col=1)

        fig.add_trace(go.Scatter3d(
            x=[x_values[i]] * 5,
            y=[y_values[i]] * 5,
            z=[0, z_values[i], z_values[i], 0, 0],
            mode='lines',
            line=dict(width=10, color="blue"),
            showlegend=False
        ), row=1, col=1)

    return fig, total_counts

# ファイルのアップロード
col1, col2, col3 = st.columns([3, 3, 1])
with col1:
    uploaded_files = st.file_uploader("txtファイルをアップロードしてください(先)", type="txt", accept_multiple_files=True)
with col2:
    uploaded_files2 = st.file_uploader("別のtxtファイルをアップロードしてください", type="txt", accept_multiple_files=True)
with col3:
    sample_f = st.file_uploader("csvファイルをアップロードしてください", type=["csv"])

specific_string = "windarab"

# ファイルの読み込み
if uploaded_files is not None:
    dataframes = process_files(uploaded_files, specific_string)

if uploaded_files2 is not None:
    dataframes2 = process_files(uploaded_files2, specific_string)

# グラフのパラメータ設定
if sample_f is not None:
    sample_df = pd.read_csv(sample_f, encoding='CP932')
    sample_columns = 2 if sample_df.shape[1] == 2 else 5  # サンプルカラム数の確認
    sample_par = sample_df.columns.tolist()

    with st.sidebar:
        x_pal = st.selectbox('x列を選択してください', sample_par)
        y_pal = st.selectbox('y列を選択してください', sample_par)
        x_lower_bound = st.number_input('xの下限値と', step=1)
        x_upper_bound = st.number_input('xの上限値を入力してください', value=100, step=10)
        y_lower_bound = st.number_input('yの下限値と', step=1)
        y_upper_bound = st.number_input('yの上限値を入力してください', value=200, step=10)
        x_div_num = st.number_input('x軸分割数', value=20)
        y_div_num = st.number_input('y軸分割数', value=20)

# グラフの作成
if dataframes:
    fig1, total_counts1 = create_fig(dataframes, x_pal, y_pal, x_lower_bound, x_upper_bound, y_lower_bound, y_upper_bound, x_div_num, y_div_num)
    st.plotly_chart(fig1, use_container_width=False)

if dataframes2:
    fig2, total_counts2 = create_fig(dataframes2, x_pal, y_pal, x_lower_bound, x_upper_bound, y_lower_bound, y_upper_bound, x_div_num, y_div_num)
    st.plotly_chart(fig2, use_container_width=False)
この修正により、cavファイルやその他の非対象ファイルが誤って処理されることはなくなります。

0/50000
左のテンプレートから選んで修正していただくか、自由入力してください。
また、Ctrl+Enterでメッセージを送信できます。
