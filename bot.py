import os
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# ログの詳細な設定（日付、ログレベル、メッセージを出力）
logging.basicConfig(
    filename='trading_bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
# コンソールにもログを表示
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logging.getLogger().addHandler(console_handler)

app = Flask(__name__)

# 環境変数からAPIキーなどを安全に取得
API_KEY = os.getenv("BROKER_API_KEY", "dummy_key")
SECRET_KEY = os.getenv("BROKER_SECRET_KEY", "dummy_secret")
ENV_MODE = os.getenv("ENV_MODE", "paper")  # paper (仮想) または live (本番)

def execute_broker_order(symbol, action, qty):
    """
    証券会社APIを呼び出して実際に注文を執行する関数
    ※各証券会社の公式SDKやAPIドキュメントに沿って中身を書き換えてください。
    """
    logging.info(f"[{ENV_MODE.upper}] 発注処理を実行中... 銘柄: {symbol}, 売買: {action}, 数量: {qty}")
    
    try:
        # --- 【ここに証券会社のAPI連携コードを記述】 ---
        # 例: Alpacaや各証券会社のクライアントを使った注文処理
        # response = trading_client.submit_order(...)
        
        # 仮の成功レスポンス
        simulated_order_id = "ORD-2026-99998888"
        logging.info(f"【発注成功】 注文ID: {simulated_order_id}")
        return True, {"order_id": simulated_order_id, "status": "filled"}
        
    except Exception as e:
        logging.error(f"【発注失敗】 エラー内容: {str(e)}")
        return False, {"error": str(e)}

@app.route("/health", methods=["GET"])
def health_check():
    """アプリが正常に稼働しているか確認用のエンドポイント"""
    return jsonify({"status": "healthy", "mode": ENV_MODE}), 200

@app.route("/signal", methods=["POST"])
def webhook_signal():
    """
    分析アプリからのシグナルを受け取るメインのエンドポイント
    期待するJSON形式:
    {
        "secret_token": "your_secure_webhook_token",
        "symbol": "7203",
        "action": "BUY",
        "qty": 100
    }
    """
    data = request.json
    if not data:
        logging.warning("不正なリクエスト: JSONデータが含まれていません")
        return jsonify({"error": "Invalid JSON payload"}), 400

    # 簡易的なセキュリティ認証（分析アプリ側と同じトークンを設定）
    client_token = data.get("secret_token")
    expected_token = os.getenv("WEBHOOK_SECRET_TOKEN", "default_secret")
    if client_token != expected_token:
        logging.warning("セキュリティ警告: 無効なWebhookトークンでのアクセス検知")
        return jsonify({"error": "Unauthorized"}), 401

    symbol = data.get("symbol")
    action = data.get("action")
    qty = data.get("qty", 100)

    # パラメータのバリデーション
    if not symbol or action not in ["BUY", "SELL"]:
        logging.warning(f"パラメータエラー: symbol={symbol}, action={action}")
        return jsonify({"error": "Missing 'symbol' or invalid 'action' (must be 'BUY' or 'SELL')"}), 400

    # 注文の実行
    success, result = execute_broker_order(symbol, action, qty)

    if success:
        return jsonify({"status": "success", "details": result}), 200
    else:
        return jsonify({"status": "error", "details": result}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    logging.info(f"自動売買Webhookサーバーを起動します (ポート: {port})")
    app.run(host="0.0.0.0", port=port)
