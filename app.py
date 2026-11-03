import streamlit as st
import pandas as pd
import numpy as np
import time

# --- ページ基本設定 ---
st.set_page_config(
    page_title="後悔裁判所 - AI Regret Court",
    page_icon="⚖️",
    layout="centered"
)

# --- スタイル調整（スマホスクショで映えるカードUI） ---
st.markdown("""
<style>
.verdict-card {
    background: linear-gradient(135deg, #1e1e2f 0%, #111119 100%);
    border: 2px solid #ff4b4b;
    border-radius: 12px;
    padding: 20px;
    color: #ffffff;
    box-shadow: 0 8px 16px rgba(255, 75, 75, 0.2);
    margin-bottom: 20px;
}
.verdict-title {
    font-size: 22px;
    font-weight: bold;
    color: #ff4b4b;
    text-align: center;
    border-bottom: 1px dashed #ff4b4b;
    padding-bottom: 8px;
}
.loss-amount {
    font-size: 32px;
    font-weight: 800;
    color: #00ffcc;
    text-align: center;
    margin: 12px 0;
}
</style>
""", unsafe_allow_html=True)

st.title("⚖️ 後悔裁判所 - AI Regret Court")
st.caption("あなたの『やらかした浪費・黒歴史』をAI法廷が公開処刑＆資産シミュレーション")

# --- サイドバー設定 ---
with st.sidebar:
    st.header("⚙️ 設定")
    api_key = st.text_input("OpenAI API Key (または Gemini)", type="password")
    st.markdown("※キーがなくてもデモ動作モードで試せます。")

# --- プリセット＆ユーザー入力 ---
presets = {
    "カスタム入力": {"desc": "", "cost": 15000, "years": 3, "target": "ビットコイン (BTC)"},
    "📱 ソシャゲの天井ガチャ課金": {"desc": "推しキャラを引くためにクレカのリボ払いでガチャを回し続けた", "cost": 30000, "years": 4, "target": "ビットコイン (BTC)"},
    "☕ 毎日なんとなく買ってたカフェラテ": {"desc": "コンビニやカフェで特に理由もなく毎日スイーツとラテを買っていた", "cost": 12000, "years": 5, "target": "オルカン (全世界株式)"},
    "🏋️ 幽霊会員だった高級ジム代": {"desc": "最初の1ヶ月しか行かなかったのに解約を面倒くさがって放置した", "cost": 14000, "years": 2, "target": "エヌビディア (NVDA)"}
}

selected_preset = st.selectbox("📌 プリセットから選ぶ（または直接入力）", list(presets.keys()))

col1, col2 = st.columns([2, 1])
with col1:
    user_desc = st.text_area(
        "やらかした浪費・怠惰の内容", 
        value=presets[selected_preset]["desc"],
        placeholder="例: パチンコで溶かした軍資金、買ったきり着ていないハイブランドの服..."
    )
with col2:
    monthly_cost = st.number_input("月換算の浪費額 (円)", value=presets[selected_preset]["cost"], step=1000)
    years = st.slider("継続年数 (年)", min_value=1, max_value=10, value=presets[selected_preset]["years"])
    target_asset = st.selectbox("もし投資していたら？", ["ビットコイン (BTC)", "エヌビディア (NVDA)", "オルカン (全世界株式)"])

execute_btn = st.button("🔥 裁判を開廷する（判決・シミュレーション・台本）", type="primary", use_container_width=True)

# --- 資産成長率の仮定ロジック（もしもシミュレーター） ---
def calculate_opportunity_loss(monthly, yrs, asset):
    total_principal = monthly * 12 * yrs
    # 年率仮定（BTC: 55%, NVDA: 45%, オルカン: 9%）
    rates = {"ビットコイン (BTC)": 0.55, "エヌビディア (NVDA)": 0.45, "オルカン (全世界株式)": 0.09}
    r = rates[asset]
    
    # 毎月積立の将来価値シミュレーション
    months = yrs * 12
    monthly_rate = (1 + r) ** (1/12) - 1
    future_val = monthly * (((1 + monthly_rate)**months - 1) / monthly_rate)
    
    chart_data = []
    current_val = 0
    current_invested = 0
    for m in range(1, months + 1):
        current_invested += monthly
        current_val = (current_val + monthly) * (1 + monthly_rate)
        if m % 3 == 0:  # 四半期ごと
            chart_data.append({
                "経過月数": f"{m}ヶ月",
                "浪費した元金": int(current_invested),
                f"{asset}だった場合の資産": int(current_val)
            })
            
    return total_principal, int(future_val), pd.DataFrame(chart_data)

# --- 実行処理 ---
if execute_btn:
    if not user_desc.strip():
        st.error("浪費・黒歴史の内容を入力してください。")
    else:
        total_lost, projected_val, df_chart = calculate_opportunity_loss(monthly_cost, years, target_asset)
        gap = projected_val - total_lost

        st.markdown("---")
        
        # 1. スクショ共有用判決カード
        st.markdown(f"""
        <div class="verdict-card">
            <div class="verdict-title">🚨 AI法廷 最終判決 🚨</div>
            <p style="text-align: center; margin-top: 10px; font-size: 14px; opacity: 0.8;">罪名: 重度の機会損失罪・現実逃避の罪</p>
            <div class="loss-amount">機会損失: 約 {gap:,} 円</div>
            <p style="text-align: center; font-size: 13px;">
                ドブに捨てた元金: <b>{total_lost:,} 円</b> ➔ もし {target_asset} なら: <b>{projected_val:,} 円</b>
            </p>
            <p style="text-align: center; font-style: italic; color: #ffbb00; margin-top: 10px;">
                「{user_desc}」という快楽の代償は、未来の純資産でした。
            </p>
        </div>
        """, unsafe_allow_html=True)

        # 2. もしもシミュレーター（グラフ）
        st.subheader("📈 複利の暴力：失われた富の軌跡")
        st.line_chart(df_chart.set_index("経過月数"), color=["#888888", "#00ffcc"])
        st.caption(f"※{target_asset}の過去平均パフォーマンスに基づく仮想推移です。")

        # 3. AIマルチ討論（毒舌検察官 vs 甘やかし弁護人）
        st.subheader("⚖️ 法廷レスバ（AIマルチ討論）")
        
        # APIキーがない場合のフォールバック（デモ表示）
        prosecutor_text = f"異議あり！被告人は『{user_desc}』などという一時的なドーパミンのために、本来なら手元に残っていたはずの【{projected_val:,}円】をドブに捨てました！これは明確に未来の自分に対する横領です！"
        defender_text = f"裁判長、異議を申し立てます！被告人はその浪費によって当時の極限ストレスを回避していたのです！もし{target_asset}を買っていたらチャートの暴落で胃に穴が空いて命を落としていた可能性があります！"
        judge_verdict = f"主文：被告人はただちにこのスクショをSNSに晒し、失われた【{gap:,}円】を心に刻んで明日から100円の無駄遣いすら戒める刑に処す！"

        with st.chat_message("user", avatar="😈"):
            st.write(f"**毒舌検察官 (AI Prosecutor):**\n\n{prosecutor_text}")
        
        with st.chat_message("assistant", avatar="😇"):
            st.write(f"**甘やかし弁護人 (AI Defender):**\n\n{defender_text}")
            
        with st.chat_message("assistant", avatar="⚖️"):
            st.write(f"**AI裁判長 最終宣告:**\n\n{judge_verdict}")

        # 4. ショート動画（TikTok/Shorts）60秒台本ワンクリック生成
        st.markdown("---")
        st.subheader("🎬 この裁判を動画化する（TikTok/Shorts 60秒台本）")
        
        script_content = f"""【タイトル案】
【絶望】{user_desc[:12]}…を我慢して{target_asset}買ってたら資産◯◯円だった件ww

【登場人物】
・検察（ずんだもん / 赤テロップ）
・弁護（四国めたん / 青テロップ）

---
(00:00〜00:05) 【フック】
検察：「おい！お前が{user_desc}に使った金、いくら損したか知ってるのだ？」

(00:05〜00:20) 【数字のインパクト】
弁護：「ちょっと！月たった{monthly_cost:,}円のささやかな楽しみじゃない！」
検察：「甘いのだ！{years}年で元金{total_lost:,}円…もし{target_asset}に突っ込んでたら【{projected_val:,}円】になってたのだ！」
弁護：「な、何倍になってるのよ…！？」

(00:20〜00:45) 【レスバ掛け合い】
検察：「差額はなんと約{gap:,}円！新車が一台どころか家買えるのだ！完全な有罪！」
弁護：「で、でも！その無駄遣いのおかげで当時のメンタルが救われたかもしれないでしょ！？」
検察：「メンタル以前に口座が爆死してるのだ！言い訳無用！」

(00:45〜00:60) 【オチ＆CTA】
検察：「判決！今すぐこの画面をスクショして反省文を投稿する刑に処すのだ！」
弁護：「みんなも過去の浪費、プロフのリンクで計算してみてね…」
---
"""
        st.text_area("ワンクリックでコピーできる台本テキスト", value=script_content, height=220)
        st.caption("※このまま動画編集ツール（VrewやCapCut等）に流し込めば1本ショート動画が完成します。")
