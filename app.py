import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# ページの設定
st.set_page_config(
    page_title="株式アルゴリズム＆シグナル分析アプリ",
    page_icon="📈",
    layout="wide"
)

st.title("📈 株式アルゴリズム＆シグナル分析アプリ")
st.markdown("GitHubとStreamlitで構築した株価分析・シグナル検知ダッシュボードです。")

# サイドバー：銘柄とパラメータの設定
st.sidebar.header("⚙️ 設定パネル")
ticker_symbol = st.sidebar.text_input("銘柄コード (日本株は末尾に .T)", "7203.T")
short_window = st.sidebar.slider("短期移動平均線 (日)", 5, 50, 25)
long_window = st.sidebar.slider("長期移動平均線 (日)", 20, 200, 75)
period_option = st.sidebar.selectbox("取得期間", ["6mo", "1y", "2y", "5y"], index=1)

# データの取得関数（キャッシュを利用して高速化）
@st.cache_data
def load_data(ticker, period):
    try:
        df = yf.download(ticker, period=period)
        return df
    except Exception as e:
        return None

if ticker_symbol:
    with st.spinner(f"{ticker_symbol} のデータを取得中..."):
        data = load_data(ticker_symbol, period_option)

    if data is not None and not data.empty:
        # yfinanceの仕様変更（マルチインデックスカラム）への対策
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        # 必要なカラムが存在するか確認
        if 'Close' in data.columns:
            # 移動平均線の計算
            data['SMA_Short'] = data['Close'].rolling(window=short_window).mean()
            data['SMA_Long'] = data['Close'].rolling(window=long_window).mean()

            # 最新のデータ値
            latest_close = float(data['Close'].iloc[-1])
            prev_short = float(data['SMA_Short'].iloc[-2])
            prev_long = float(data['SMA_Long'].iloc[-2])
            curr_short = float(data['SMA_Short'].iloc[-1])
            curr_long = float(data['SMA_Long'].iloc[-1])

            # シグナル判定ロジック（ゴールデンクロス / デッドクロス）
            signal = "様子見 (Hold) ⏳"
            signal_color = "normal"
            if prev_short <= prev_long and curr_short > curr_long:
                signal = "買いシグナル (Buy) 🚀"
                signal_color = "inverse"
            elif prev_short >= prev_long and curr_short < curr_long:
                signal = "売りシグナル (Sell) ⚠️"
                signal_color = "off"

            # 画面上部への結果表示
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="対象銘柄", value=ticker_symbol.upper())
            with col2:
                st.metric(label="判定シグナル", value=signal)

            st.subheader("📊 株価チャート & 移動平均線")

            # Plotlyによるインタラクティブなチャート描画
            fig = go.Figure()
            
            # 終値ライン
            fig.add_trace(go.Scatter(
                x=data.index, y=data['Close'], 
                name='終値 (Close)', 
                line=dict(color='#29b5e8', width=1.5)
            ))
            # 短期移動平均線
            fig.add_trace(go.Scatter(
                x=data.index, y=data['SMA_Short'], 
                name=f'短期 SMA ({short_window})', 
                line=dict(color='#ffaa00', width=1.5)
            ))
            # 長期移動平均線
            fig.add_trace(go.Scatter(
                x=data.index, y=data['SMA_Long'], 
                name=f'長期 SMA ({long_window})', 
                line=dict(color='#ff4b4b', width=1.5)
            ))
            
            fig.update_layout(
                xaxis_title="日付",
                yaxis_title="株価",
                template="plotly_dark",
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig, use_container_width=True)

            # 生データのプレビュー（エキスパンダー）
            with st.expander("📁 取得した直近のデータを表示"):
                st.dataframe(data.tail(10))

        else:
            st.error("データのフォーマットエラーが発生しました。別の銘柄コードをお試しください。")
    else:
        st.error(f"「{ticker_symbol}」のデータが見つかりませんでした。正しい銘柄コード（例: 7203.T, AAPL, MSFT）を入力してください。")
