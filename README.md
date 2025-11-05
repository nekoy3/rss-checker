# RSS Checker

ブログの更新を監視し、一定期間更新がない場合にDiscordで通知するツール

## 🎯 概要

RSS Checkerは、ブログのRSSフィードを定期的にチェックし、設定した日数以上更新がない場合にDiscordに通知を送信します。将来的にはDiscord Botとして拡張し、AIによるブログ記事の提案やDiscordからの記事投稿機能も実装予定です。

## ✨ 機能

### 現在の機能
- ブログのRSSフィード監視
- 設定可能な通知しきい値（日数）
- Discord Webhook/Bot経由での通知
- 柔軟な設定ファイル管理

### 今後の予定機能
- 🤖 Discord Bot化による対話機能
- 🧠 AIによるブログ記事案の提案
- 📝 Discordから直接ブログ記事を投稿
- ⏰ カスタマイズ可能なスケジュール設定

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
```

### 4. 設定の確認

```bash
python config.py
```

## 📖 使い方

### 基本的な使用方法

（実装予定）

```bash
# 手動でチェックを実行
python main.py

# Bot として起動（将来の機能）
python bot.py
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
  - `openai_api_key`: OpenAI APIキー（ブログ記事案の生成用）

- `[blog_api]`
  - `api_url`: ブログのAPI URL（記事投稿用）
  - `api_user`: APIユーザー名
  - `api_password`: APIパスワード/トークン

## 🏗️ プロジェクト構造

```
rss-checker/
├── config.py              # 設定ファイル読み込みモジュール
├── rss.conf              # 設定ファイル（gitignore済み）
├── rss.conf.example      # 設定ファイルのテンプレート
├── .gitignore            # Git除外設定
├── README.md             # このファイル
└── requirements.txt      # Python依存関係（今後作成）
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

## 📝 ライセンス

MIT License

## 👤 作成者

nekoy3

## 🔗 リンク

- GitHub: https://github.com/nekoy3/rss-checker
