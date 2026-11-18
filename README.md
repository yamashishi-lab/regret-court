# Trading Bot Webhook Server

TradingViewや自作の分析アプリからのシグナル（JSON）を受け取り、証券会社API経由で自動発注を行うFlaskサーバーです。

## 🚀 セットアップ方法

1. リポジトリをクローンまたはダウンロード
2. 仮想環境の作成と有効化
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windowsは venv\Scripts\activate
