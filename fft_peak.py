import streamlit as st
import pandas as pd
import numpy as np
from scipy.signal import stft, find_peaks
import matplotlib.pyplot as plt
import io
import re

def try_parse_header(file, max_check_lines=10):
    """
    アップロードファイルの先頭max_check_lines行を読み込み、
    どの行がヘッダーっぽいか推定する。
    戻り値：推定ヘッダー行番号（0始まり）、またはNone
    """
    # バイナリ読み込み → テキスト変換
    file.seek(0)
    sample = file.read().decode(errors='ignore').splitlines()
    if len(sample) < max_check_lines:
        lines_to_check = len(sample)
    else:
        lines_to_check = max_check_lines

    # 各行でカラムをカンマ区切りで分割し、数字か文字かを判定
    header_scores = []
    for i in range(lines_to_check):
        line = sample[i]
        cells = line.split(',')
        n_numeric = 0
        n_total = len(cells)
        for c in cells:
            try:
                float(c)
                n_numeric += 1
            except:
                pass
        # 数字が少ないほどヘッダーっぽいと仮定（数字が多い行はデータ行）
        numeric_ratio = n_numeric / n_total if n_total > 0 else 0
        header_scores.append((i, numeric_ratio))

    # 数字率が最も低い行をヘッダー候補とする
    header_scores.sort(key=lambda x: x[1])
    guessed_header = header_scores[0][0] if header_scores else None
    return guessed_header

def load_csv(file, header_row, data_start_offset=0):
    """
    file: ファイルオブジェクト
    header_row: ヘッダー行番号 (0始まり)
    data_start_offset: ヘッダー行の次から何行スキップしてデータ開始か（0ならヘッダー直後からデータ）

    ヘッダー行から data_start_offset 行スキップしてからデータを読み込みます。
    """
    file.seek(0)
    # ファイル全行読み込み
    lines = file.read().decode(errors='ignore').splitlines()

    # ヘッダー行の列名取得
    header_line = lines[header_row]
    columns = [h.strip() for h in header_line.split(",")]

    # データ開始行
    data_start_line = header_row + 1 + data_start_offset

    # データ部分を抽出
    data_lines = lines[data_start_line:]

    from io import StringIO
    data_str = "\n".join(data_lines)
    data_io = StringIO(data_str)

    # pandasで読み込み（headerなし、カラム名を指定）
    df = pd.read_csv(data_io, header=None, names=columns)

    return df

def detect_time_column(df):
    """
    数値列の中から単調増加かつ等間隔に近い列を時間軸候補とする。
    """
    candidates = []
    for col in df.columns:
        s = df[col]
        # 数値型かチェック
        if pd.api.types.is_numeric_dtype(s):
            # 欠損なしかチェック
            if s.isnull().any():
                continue
            # 単調増加かチェック
            diffs = np.diff(s)
            if np.all(diffs >= -1e-8):  # 少しの誤差は許容
                # 間隔の標準偏差が小さいか
                std_diff = np.std(diffs)
                mean_diff = np.mean(diffs)
                if mean_diff > 0 and std_diff / mean_diff < 0.1:
                    candidates.append((col, std_diff / mean_diff))
    # std_diff/mean_diffが小さい順にソート
    candidates.sort(key=lambda x: x[1])
    if candidates:
        return candidates[0][0]
    else:
        return None

def plot_spectrogram(f, t, Zxx):
    fig, ax = plt.subplots(figsize=(10, 4))
    pcm = ax.pcolormesh(t, f, np.abs(Zxx), shading='gouraud')
    ax.set_ylabel('Frequency [Hz]')
    ax.set_xlabel('Time [sec]')
    fig.colorbar(pcm, ax=ax, label='Magnitude')
    ax.set_ylim(0, max(f))
    return fig

def peak_hold_detection(frequencies, times, spectrogram, target_freq, freq_tolerance=1.0, height=None):
    freq_idx = np.where((frequencies >= target_freq - freq_tolerance) & (frequencies <= target_freq + freq_tolerance))[0]
    if len(freq_idx) == 0:
        st.error("指定した周波数付近にデータがありません。")
        return None, None
    
    band_power = spectrogram[freq_idx, :].max(axis=0)
    peaks, _ = find_peaks(band_power, height=height)
    peak_times = times[peaks]

    fig, ax = plt.subplots(figsize=(10, 3))
    ax.plot(times, band_power, label=f'{target_freq} Hz band power (peak hold)')
    ax.plot(peak_times, band_power[peaks], "x", label='Detected Peaks')
    ax.set_xlabel('Time [sec]')
    ax.set_ylabel('Magnitude')
    ax.legend()
    return fig, peak_times

def parse_time_column(series):
    """
    時間軸の文字列シリーズを受け取り、
    単位付き（例：'0.05msec', '10ms', '0.1 s'）または単位なし数値文字列を
    秒単位のfloat配列に変換して返す関数。
    """
    time_values = []
    pattern = re.compile(r"^\s*([-+]?[0-9]*[.,]?[0-9]+(?:[eE][-+]?[0-9]+)?)\s*([a-zA-Z]*)\s*$")

    for v in series.astype(str):
        m = pattern.match(v)
        if m:
            val_str = m.group(1).replace(',', '.')  # カンマをドットに置換
            try:
                val = float(val_str)
            except:
                time_values.append(np.nan)
                continue

            unit = m.group(2).lower()

            if unit in ['', 's', 'sec', 'second', 'seconds']:
                factor = 1.0
            elif unit in ['ms', 'msec', 'millisecond', 'milliseconds']:
                factor = 1e-3
            elif unit in ['us', 'usec', 'microsecond', 'microseconds']:
                factor = 1e-6
            elif unit in ['ns', 'nanosecond', 'nanoseconds']:
                factor = 1e-9
            else:
                factor = 1.0  # 不明な単位は無変換

            time_values.append(val * factor)
        else:
            time_values.append(np.nan)

    return np.array(time_values)

def main():
    st.title("FFTスペクトログラム＆ピークホールド検出（ヘッダー＆列自動検出対応）")

    st.markdown("""
    - CSVアップロード前に「ヘッダー行番号」を指定または自動検出可能です。
    - 時間軸列・信号列の自動候補も表示し、手動選択可能です。
    """)

    # 1. ヘッダー行番号の入力または自動検出
    header_row_input = st.number_input("ヘッダー行番号を指定してください (0始まり、未指定は-1)", value=-1, step=1)

    uploaded_file = st.file_uploader("CSVファイルをアップロードしてください", type=["csv"])
    if uploaded_file is not None:

        # 自動検出ボタン
        if header_row_input == -1:
            if st.button("ヘッダー行自動検出"):
                guessed_header = try_parse_header(uploaded_file)
                if guessed_header is not None:
                    st.success(f"自動検出されたヘッダー行: {guessed_header} 行目 (0始まり)")
                    header_row = guessed_header
                else:
                    st.warning("ヘッダー行の自動検出に失敗しました。")
                    header_row = 0
            else:
                st.info("ヘッダー行自動検出ボタンを押してください")
                return
        else:
            header_row = header_row_input

        # CSV読み込み
        try:
            df = load_csv(uploaded_file, header_row)
        except Exception as e:
            st.error(f"CSV読み込みエラー: {e}")
            return

        st.write("読み込んだCSVの先頭5行")
        st.dataframe(df.head())

        # 2. 時間軸列の自動検出候補
        time_col_auto = detect_time_column(df)
        st.write(f"自動検出された時間軸候補列: {time_col_auto}")

        # 時間軸列の選択
        time_col = st.selectbox("時間軸の列を選択してください", options=df.columns, index=df.columns.get_loc(time_col_auto) if time_col_auto in df.columns else 0)
        raw_time_series = df[time_col]

        # ここで単位付き・単位なし対応のパース関数を使う
        time = parse_time_column(raw_time_series)

        # nanがある場合は適宜処理（ここでは除去例）
        valid_idx = ~np.isnan(time)
        time = time[valid_idx]

        # 時間軸に対応する信号データも同様に抽出
        # 信号列は後のmultiselectで選択されるため、その時にvalid_idxを使って信号も絞る処理を追加すると良い

        # サンプリング周波数計算
        fs = 1 / np.mean(np.diff(time)) * 1000
        st.write(f"サンプリング周波数: {fs:.2f} Hz")

        # STFTパラメータ調整UI
        nperseg = st.slider("STFTの窓幅 (nperseg)", min_value=64, max_value=2048, value=256, step=64)
        noverlap = st.slider("STFTの窓重なり (noverlap)", min_value=0, max_value=nperseg-1, value=nperseg//2)

        target_freq = st.number_input("ピークホールド検出したい周波数をHzで入力してください", min_value=0.0, max_value=fs/2, value=50.0, step=0.1)
        freq_tolerance = st.number_input("周波数許容範囲 (±Hz)", min_value=0.1, max_value=10.0, value=1.0, step=0.1)

        for col in signal_cols:
            st.subheader(f"信号列: {col}")
            signal = df[col].values

            # STFT計算
            f, t, Zxx = stft(signal, fs=fs, window = "hann" ,nperseg=nperseg, noverlap=noverlap)

            # スペクトログラム表示
            fig_spec = plot_spectrogram(f, t, Zxx)
            st.pyplot(fig_spec)

            # ピークホールド検出ボタン
            if st.button(f"{col} のピークホールド検出実行", key=col):
                fig_peaks, peak_times = peak_hold_detection(f, t, np.abs(Zxx), target_freq, freq_tolerance)
                if fig_peaks is not None:
                    st.pyplot(fig_peaks)
                    st.write(f"{col} の検出したピークタイミング（秒）:")
                    st.write(peak_times)
            
            # 信号全体のFFT計算
            N = len(signal)
            # FFT実行
            fft_vals = np.fft.rfft(signal)
            # 周波数軸生成
            freqs = np.fft.rfftfreq(N, d=1/fs)
            # 振幅スペクトル（正規化）
            amplitude = np.abs(fft_vals) / N * 2  # 両側スペクトルの片側なので2倍。ただし直流成分は2倍しない等の調整も可能。

            # 振幅スペクトルプロット
            fig_fft, ax_fft = plt.subplots(figsize=(10, 4))
            ax_fft.plot(freqs, amplitude)
            ax_fft.set_xlabel('Frequency [Hz]')
            ax_fft.set_ylabel('Amplitude')
            ax_fft.set_title(f'FFT振幅スペクトル: {col}')
            ax_fft.set_xlim(0, fs/2)
            st.pyplot(fig_fft)

if __name__ == "__main__":
    main()
