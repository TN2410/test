import os
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats

# --- 1つ目の機能の関数 ---

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
    return dataframes, skiprows

def create_fig(dataframes, x_pal, y_pal, x_lower_bound, x_upper_bound, y_lower_bound, y_upper_bound, x_div_num, y_div_num, skiprows):
    # --- （省略。元の create_fig 関数の中身をそのまま入れてください） ---
    # ここは元のコードをコピペしてください。
    pass  # 省略のためのダミー

def feature_one():
    st.title("windarab or dpu 積算データ")

    uploaded_files = st.file_uploader("txtファイルをアップロードしてください(先)", type="txt", accept_multiple_files=True, key="uf1")
    uploaded_files2 = st.file_uploader("別のtxtファイルをアップロードしてください", type="txt", accept_multiple_files=True, key="uf2")
    sample_f = st.file_uploader("csvファイルをアップロードしてください", type=["csv"], key="uf3")

    specific_string = "windarab"

    dataframes, skiprows = None, 0
    if uploaded_files:
        with st.spinner("ファイル処理中..."):
            dataframes, skiprows = process_files(uploaded_files, specific_string)
    if uploaded_files2:
        with st.spinner("ファイル処理中..."):
            dataframes2, skiprows = process_files(uploaded_files2, specific_string)

    if sample_f is not None:
        sample_df = pd.read_csv(sample_f, encoding='CP932')
        sample_columns = 5 if skiprows == 0 else 2
        sample_par = sample_df.iloc[:, sample_columns].tolist()
        sample_par = list(filter(pd.notna, sample_par))

        if skiprows == 0:
            initial_x_pal, initial_y_pal = "NE", "P_Manifold1"
            initial_x_lower_bound, initial_x_upper_bound = 0, 10000
            initial_y_lower_bound, initial_y_upper_bound = 0, 250
        else:
            initial_x_pal, initial_y_pal = "nmot", "pboost"
            initial_x_lower_bound, initial_x_upper_bound = 0, 8000
            initial_y_lower_bound, initial_y_upper_bound = 0, 2000

        with st.sidebar:
            x_pal = st.selectbox('x列を選択してください', sample_par, index=sample_par.index(initial_x_pal))
            y_pal = st.selectbox('y列を選択してください', sample_par, index=sample_par.index(initial_y_pal))
            x_lower_bound = st.number_input('xの下限値を入力してください', value=initial_x_lower_bound, step=1)
            x_upper_bound = st.number_input('xの上限値を入力してください', value=initial_x_upper_bound, step=10)
            y_lower_bound = st.number_input('yの下限値を入力してください', value=initial_y_lower_bound, step=1)
            y_upper_bound = st.number_input('yの上限値を入力してください', value=initial_y_upper_bound, step=10)
            x_div_num = st.number_input('x軸分割数', value=20)
            y_div_num = st.number_input('y軸分割数', value=20)

    if dataframes:
        with st.spinner("グラフを作成中..."):
            fig1, z_values1, normalized_z_values1, total_z_value1 ,x_values1, y_values1, all_z_values1 = create_fig(
                dataframes, x_pal, y_pal, x_lower_bound, x_upper_bound,
                y_lower_bound, y_upper_bound, x_div_num, y_div_num, skiprows)
            st.plotly_chart(fig1)

            # CSV出力ボタン
            output_data1 = {
                'x': x_values1,
                'y': y_values1,
                'z': all_z_values1,
                'normalized_z': normalized_z_values1
            }
            output_df1 = pd.DataFrame(output_data1)
            output_csv1 = output_df1.to_csv(index=False)
            st.download_button(
                label=f"{uploaded_files[0].name}他のCSVをダウンロード",
                data=output_csv1,
                file_name=f"{uploaded_files[0].name}.csv",
                mime='text/csv'
            )

    if dataframes2:
        with st.spinner("別のグラフを作成中..."):
            fig2, z_values2, normalized_z_values2, total_z_value2 ,x_values2, y_values2, all_z_values2 = create_fig(
                dataframes2, x_pal, y_pal, x_lower_bound, x_upper_bound,
                y_lower_bound, y_upper_bound, x_div_num, y_div_num, skiprows)
            st.plotly_chart(fig2)

            # CSV出力ボタン
            output_data2 = {
                'x': x_values2,
                'y': y_values2,
                'z': all_z_values2,
                'normalized_z': normalized_z_values2
            }
            output_df2 = pd.DataFrame(output_data2)
            output_csv2 = output_df2.to_csv(index=False)
            st.download_button(
                label=f"{uploaded_files2[0].name}他のCSVをダウンロード",
                data=output_csv2,
                file_name=f"{uploaded_files2[0].name}.csv",
                mime='text/csv'
            )

    # 有意差検定
    if dataframes and dataframes2 and normalized_z_values1 and normalized_z_values2:
        t_statistic, p_value_t = stats.ttest_ind(normalized_z_values1, normalized_z_values2)
        st.write(f"t統計量: {t_statistic:.3f}, p値: {p_value_t:.3g}")
        if p_value_t < 0.05:
            st.write("有意差あり")

        u_statistic, p_value_u = stats.mannwhitneyu(normalized_z_values1, normalized_z_values2, alternative='two-sided')
        st.write(f"U統計量: {u_statistic:.3f}, p値: {p_value_u:.3g}")
        if p_value_u < 0.05:
            st.write("有意差あり")

# --- 2つ目の機能の関数 ---

def feature_two():
    st.title("ドラッグ＆ドロップしたファイルのパラメータ抽出＆ヒストグラム")

    uploaded_files = st.file_uploader("ファイルを複数選択してください", accept_multiple_files=True, type=["txt", "csv"], key="uf_second")

    parameter = st.text_input("抽出するパラメータ名を入力してください", value="SFTP")

    if uploaded_files and parameter:
        df_all = pd.DataFrame()
        maxmax = None
        maxfile = None

        for uploaded_file in uploaded_files:
            try:
                df = pd.read_csv(uploaded_file, sep="\t", encoding='utf-8', low_memory=False)
                if parameter in df.columns:
                    max_val = df[parameter].astype(float).max()
                    if maxmax is None or max_val > maxmax:
                        maxmax = max_val
                        maxfile = uploaded_file.name
                    df_param = df[parameter].astype(float)
                    df_all = pd.concat([df_all, df_param], axis=0)
            except Exception as e:
                st.warning(f"{uploaded_file.name} の読み込みでエラー: {e}")

        if df_all.empty:
            st.warning("指定したパラメータのデータが見つかりません。")
        else:
            alldata = np.array(df_all)
            st.write(f"最大値: {maxmax} （ファイル: {maxfile}）")
            st.write(f"データ数: {len(alldata)}")

            min_val = st.number_input("ヒストグラムの最小値", value=0.0, format="%.3f")
            max_val = st.number_input("ヒストグラムの最大値", value=10.0, format="%.3f")
            bins_num = st.number_input("ビンの数（分割数）", min_value=1, max_value=1000, value=10, step=1)

            if min_val >= max_val:
                st.error("最小値は最大値より小さく設定してください。")
            else:
                filtered_data = alldata[(alldata >= min_val) & (alldata <= max_val)]
                bins = np.linspace(min_val, max_val, bins_num + 1)
                counts, bin_edges = np.histogram(filtered_data, bins=bins)

                fig = make_subplots(rows=1, cols=1)
                fig.add_trace(
                    go.Bar(
                        x=bin_edges[:-1],
                        y=counts,
                        width=(bin_edges[1] - bin_edges[0]),
                        marker_color='navy',
                        opacity=0.6,
                        name='度数'
                    ),
                    row=1, col=1
                )
                fig.update_layout(
                    title=f"全{len(filtered_data)/3600:.4g}時間",
                    xaxis_title=parameter,
                    yaxis_title="time(sec)",
                    bargap=0.1,
                    template="plotly_white",
                    font=dict(family="Meiryo", size=14)
                )
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("左上の「ファイルを選択」から複数ファイルをアップロードしてください。")

# --- メイン処理 ---

def main():
    st.sidebar.title("機能選択")
    option = st.sidebar.selectbox("機能を選んでください", ("windarab or dpu 積算データ", "パラメータ抽出＆ヒストグラム"))

    if option == "windarab or dpu 積算データ":
        feature_one()
    else:
        feature_two()

if __name__ == "__main__":
    main()