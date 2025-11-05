# RSS Checker

ブログの更新を監視し、一定期間更新がない場合にDiscordで通知するツール

## 🎯 概要

RSS Checkerは、ブログのRSSフィードを定期的にチェックし、設定した日数以上更新がない場合にDiscordに通知を送信します。将来的にはDiscord Botとして拡張し、AIによるブログ記事の提案やDiscordからの記事投稿機能も実装予定です。

## ✨ 機能

### 現在の機能
- ✅ ブログのRSSフィード監視
- ✅ 設定可能な通知しきい値（日数）
- ✅ Discord Webhook/Bot経由での通知
- ✅ 柔軟な設定ファイル管理
- ✅ スケジュール実行（毎日指定時刻に自動チェック）
- ✅ 設定テスト機能

### 今後の予定機能
- 🤖 Discord Bot化による対話機能
- 🧠 Gemini AIによるブログ記事案の提案
- 📝 Discordから直接ブログ記事を投稿
- 📊 更新履歴の可視化

## 🚀 セットアップ

### 1. リポジトリのクローン

```bash
git clone https://github.com/nekoy3/rss-checker.git
cd rss-checker
```

### 2. Python環境のセットアップ

```bash
python -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 設定ファイルの作成

```bash
cp rss.conf.example rss.conf
```

`rss.conf`を編集して、以下の情報を設定：

```ini
[blog]
url = https://your-blog.com
rss_feed_url = https://your-blog.com/feed

[discord]
# Webhook方式（シンプル）
webhook_url = https://discord.com/api/webhooks/YOUR_WEBHOOK_URL

# または Bot方式（将来の拡張機能用）
# bot_token = YOUR_BOT_TOKEN
# channel_id = YOUR_CHANNEL_ID

[notification]
threshold_days = 7
notification_time = 19:00

[ai]
# 将来のAI機能用（Google Gemini API）
# gemini_api_key = YOUR_GEMINI_API_KEY
```

### 4. Discord Webhookの取得方法

1. Discordサーバーの設定を開く
2. 「連携サービス」→「ウェブフック」を選択
3. 「新しいウェブフック」をクリック
4. 名前を設定し、通知先のチャンネルを選択
5. 「ウェブフックURLをコピー」をクリック
6. `rss.conf`の`webhook_url`に貼り付け

### 5. (オプション) Gemini APIキーの取得

将来のAI機能用：

1. [Google AI Studio](https://aistudio.google.com/) にアクセス
2. 「Get API key」をクリック
3. APIキーを作成してコピー
4. `rss.conf`の`gemini_api_key`に貼り付け

**無料枠:** 1日1500リクエストまで無料！

### 6. 設定のテスト

```bash
python main.py --mode test
```

これで以下をテストします：
- 設定ファイルの読み込み
- RSSフィードへのアクセス
- Discord通知の送信

## 📖 使い方

### 基本的な使用方法

```bash
# 1回だけチェックを実行
python main.py

# または明示的に
python main.py --mode once

# 毎日指定時刻に自動実行（スケジュールモード）
python main.py --mode schedule

# 設定テスト
python main.py --mode test
```

### スケジュールモードの詳細

`--mode schedule`で起動すると、`rss.conf`の`notification_time`で設定した時刻に毎日自動的にチェックを実行します。

```bash
# バックグラウンドで実行（Linux/Mac）
nohup python main.py --mode schedule > rss-checker.log 2>&1 &

# または systemd サービスとして登録（推奨）
```

### 個別モジュールのテスト

```bash
# RSSフィードのチェック
python rss_checker.py https://your-blog.com/feed 7

# Discord通知のテスト（Webhook）
python discord_notifier.py https://discord.com/api/webhooks/...

# Discord通知のテスト（Bot）
python discord_notifier.py YOUR_BOT_TOKEN YOUR_CHANNEL_ID
```

## 🔧 設定ファイル (rss.conf)

### 必須設定

- `[blog]`
  - `url`: ブログのURL
  - `rss_feed_url`: RSSフィードのURL（省略可能）

- `[discord]`
  - `webhook_url`: Discord Webhook URL **または**
  - `bot_token` + `channel_id`: Discord Bot設定

- `[notification]`
  - `threshold_days`: 通知しきい値（日数）
  - `notification_time`: チェック時刻（HH:MM形式）

### オプション設定（将来の機能用）

- `[ai]`
  - `gemini_api_key`: Google Gemini APIキー（ブログ記事案の生成用）

- `[blog_api]`
  - `api_url`: ブログのAPI URL（記事投稿用）
  - `api_user`: APIユーザー名
  - `api_password`: APIパスワード/トークン

## 🏗️ プロジェクト構造

```
rss-checker/
├── main.py                   # メインスクリプト（実行エントリーポイント）
├── config.py                 # 設定ファイル読み込みモジュール
├── rss_checker.py           # RSS監視モジュール
├── discord_notifier.py      # Discord通知モジュール
├── rss.conf                 # 設定ファイル（gitignore済み）
├── rss.conf.example         # 設定ファイルのテンプレート
├── .gitignore               # Git除外設定
├── README.md                # このファイル
└── requirements.txt         # Python依存関係
```

## 🤔 開発方針について

### Webhook vs Bot

このプロジェクトは将来的な拡張を考慮し、**Discord Bot**として開発することを推奨します。

**Bot方式の利点：**
- `/blog suggest` でAIに記事案を依頼
- `/blog post` でDiscordから記事投稿
- `/blog status` で更新状況の確認
- より柔軟な対話型の機能実装が可能

**Webhook方式：**
- シンプルで導入が簡単
- 通知のみの用途には十分
- Bot方式への移行も容易

現在はWebhook/Botの両方に対応していますが、将来の対話機能を考えるとBot推奨です。

## �� トラブルシューティング

### RSSフィードが読み取れない

```bash
# RSSフィードのURLを直接テスト
python rss_checker.py https://your-blog.com/feed
```

- URLが正しいか確認
- RSSフィードが公開されているか確認
- ネットワーク接続を確認

### Discord通知が届かない

```bash
# Discord設定をテスト
python main.py --mode test
```

- Webhook URLが正しいか確認
- チャンネルの権限を確認
- Botの場合、トークンとチャンネルIDを確認

## 📝 ライセンス

MIT License

## 👤 作成者

nekoy3

## 🔗 リンク

- GitHub: https://github.com/nekoy3/rss-checker
- Google AI Studio: https://aistudio.google.com/
