# RSS Checker

RSS Checker は、ブログのRSSフィードを監視し、指定期間更新がない場合にDiscordに通知するPythonアプリケーションです。Discord Botとして常時稼働し、スラッシュコマンドとAIによるブログテーマ提案機能を提供します。

## 機能

### 🤖 Discord Bot機能
- **スラッシュコマンド対応**
  - `/blog_check` - ブログの更新状況を今すぐチェック
  - `/blog_suggest` - AIにブログテーマを提案してもらう
  - `/blog_status` - BotとRSSチェッカーの状態を表示
- **自動通知** - 毎日指定時刻にRSSフィードをチェック
- **@everyone メンション** - しきい値を超えた場合の通知

### 🧠 AI機能
- Google Gemini APIによるブログテーマ提案
- 最近の投稿を考慮した提案
- 特定テーマに基づいた提案

### 📊 RSS監視
- RSSフィードから最新記事の更新日時を取得
- 指定したしきい値（日数）以上更新がない場合に通知
- 複数の日付形式に対応

## 必要要件

- Python 3.7以上
- pip（Pythonパッケージ管理ツール）
- Discord Bot Token（Bot機能を使用する場合）
- Google Gemini API Key（AI機能を使用する場合）

## インストール

1. リポジトリをクローン：
```bash
git clone https://github.com/nekoy3/rss-checker.git
cd rss-checker
```

2. 仮想環境を作成（推奨）：
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# または
venv\Scripts\activate  # Windows
```

3. 必要なパッケージをインストール：
```bash
pip install -r requirements.txt
```

## 設定

1. `rss.conf.example` をコピーして `rss.conf` を作成：
```bash
cp rss.conf.example rss.conf
```

2. `rss.conf` を編集して、以下の情報を設定：

```ini
[blog]
# ブログのURL（表示用）
url = https://example.com

# RSSフィードのURL
rss_feed_url = https://example.com/feed

[discord]
# Discord Bot Token（必須）
bot_token = YOUR_DISCORD_BOT_TOKEN
channel_id = 1234567890123456789

# Webhook URL（オプション：main.pyのWebhook方式で使用）
webhook_url = https://discord.com/api/webhooks/...

[notification]
# 通知しきい値（日数）
threshold_days = 7

# 通知時刻（HH:MM形式）
notification_time = 19:00

[ai]
# Google Gemini API Key（AI機能を使用する場合）
gemini_api_key = YOUR_GEMINI_API_KEY
```

### Discord Botのセットアップ

1. [Discord Developer Portal](https://discord.com/developers/applications) にアクセス
2. 新しいApplicationを作成
3. Botセクションで以下を有効化：
   - MESSAGE CONTENT INTENT
4. OAuth2 URLジェネレーターで以下を選択：
   - Scopes: `bot`, `applications.commands`
   - Bot Permissions: `Send Messages`, `Embed Links`, `Mention Everyone`
5. 生成されたURLでBotをサーバーに招待

### Gemini APIのセットアップ

1. [Google AI Studio](https://makersuite.google.com/app/apikey) にアクセス
2. APIキーを作成
3. `rss.conf` の `gemini_api_key` に設定

## 使い方

### Discord Bot（推奨）

常時稼働するDiscord Botとして実行：

```bash
python bot.py
```

#### スラッシュコマンド

Discord内で以下のコマンドが使用できます：

- `/blog_check` - ブログの更新状況を今すぐチェック
- `/blog_suggest` - AIにブログテーマを提案してもらう（ランダム）
- `/blog_suggest theme:技術` - 特定テーマでAIに提案してもらう
- `/blog_status` - BotとRSSチェッカーの状態を表示

### 従来の実行方法

#### 一度だけ実行

```bash
python main.py --mode once
```

#### スケジュール実行

指定した時刻に毎日自動チェックを実行：

```bash
python main.py --mode schedule
```

#### 設定テスト

設定ファイルと接続をテスト：

```bash
python main.py --mode test
```

## systemdサービスとして実行（Linux）

1. サービスファイルがすでに `/etc/systemd/system/rss-checker.service` に配置されています

2. サービスを有効化して起動：
```bash
sudo systemctl enable rss-checker
sudo systemctl start rss-checker
```

3. ステータス確認：
```bash
sudo systemctl status rss-checker
```

4. ログ確認：
```bash
tail -f ~/rss-checker/rss-checker.log
# または
journalctl -u rss-checker -f
```

5. サービスの再起動：
```bash
sudo systemctl restart rss-checker
```

## ファイル構成

```
rss-checker/
├── bot.py              # Discord Botメインファイル（推奨）
├── main.py             # 従来の実行ファイル
├── config.py           # 設定読み込みモジュール
├── rss_checker.py      # RSSフィード監視モジュール
├── discord_notifier.py # Discord通知モジュール
├── ai_suggester.py     # AI提案モジュール
├── rss.conf            # 設定ファイル（要作成）
├── rss.conf.example    # 設定ファイルの例
├── requirements.txt    # Python依存パッケージ
└── README.md           # このファイル
```

## ログ

ログは以下の場所に出力されます：
- コンソール出力（標準出力）
- `rss-checker.log`（ファイル出力）

ログレベル：
- INFO: 通常の動作ログ
- WARNING: 通知送信時など
- ERROR: エラー発生時

## トラブルシューティング

### RSSフィードが取得できない

- RSSフィードのURLが正しいか確認
- ネットワーク接続を確認
- フィードが有効なXML形式か確認

### Discord通知が送信されない

- Bot Tokenが正しいか確認
- Channel IDが正しいか確認
- Botがサーバーに招待されているか確認
- Botに必要な権限があるか確認（Send Messages, Embed Links, Mention Everyone）

### スラッシュコマンドが表示されない

- Botが正常に起動しているか確認（`✓ Synced X slash command(s)` のログを確認）
- 起動後、コマンドの同期に数分かかることがあります
- Discord側のキャッシュをクリア（Discordアプリを再起動）

### AI機能が使えない

- `rss.conf` に `gemini_api_key` が設定されているか確認
- APIキーが有効か確認
- ネットワーク接続を確認
- Gemini APIの利用制限に達していないか確認

### 日付の解析エラー

- RSSフィードの日付形式が対応しているか確認
- 複数の日付形式に対応していますが、必要に応じて `rss_checker.py` の `_extract_date()` メソッドを修正

## ライセンス

MIT License

## 作者

nekoy3
