#!/usr/bin/env python3
"""
RSS Checker Discord Bot
Monitors blog RSS and provides interactive commands
"""

import re
import discord
from discord.ext import commands, tasks
from discord import app_commands
import logging
from datetime import datetime, time as dt_time
import asyncio

from config import load_config
from rss_checker import RSSChecker
from ai_suggester import AISuggester
from hatena_blog_api import HatenaBlogAPI

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load configuration
config = load_config()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Initialize modules
rss_checker = RSSChecker(config.rss_feed_url or config.blog_url)
ai_suggester = AISuggester(config.gemini_api_key) if config.gemini_api_key else None


@bot.event
async def on_ready():
    """Bot ready event"""
    logger.info(f'✓ Bot logged in as {bot.user}')
    logger.info(f'✓ Connected to {len(bot.guilds)} server(s)')
    
    # Sync slash commands (guild-specific for faster updates)
    try:
        # Sync to all guilds the bot is in
        for guild in bot.guilds:
            bot.tree.copy_global_to(guild=guild)
            synced = await bot.tree.sync(guild=guild)
            logger.info(f'✓ Synced {len(synced)} command(s) to guild {guild.name} (ID: {guild.id})')
        
        # Also sync globally (takes up to 1 hour)
        synced_global = await bot.tree.sync()
        logger.info(f'✓ Synced {len(synced_global)} command(s) globally')
    except Exception as e:
        logger.error(f'✗ Failed to sync commands: {e}')
    
    # Start scheduled check
    scheduled_check.start()
    logger.info(f'✓ Scheduled check started (will run at {config.notification_time})')


# Store message IDs for suggestion tracking
suggestion_messages = {}

@bot.event
async def on_raw_reaction_add(reaction: discord.RawReactionActionEvent):
    """Handle reactions to blog suggestion messages"""
    if reaction.user_id == bot.user.id:
        return
    
    if reaction.message_id not in suggestion_messages:
        return
    
    if reaction.emoji.name not in ['1️⃣', '2️⃣', '3️⃣']:
        return
    
    logger.info(f"Reaction {reaction.emoji.name} detected on suggestion message")
    
    try:
        channel = bot.get_channel(reaction.channel_id)
        message = await channel.fetch_message(reaction.message_id)
        suggestions_data = suggestion_messages[reaction.message_id]
        
        emoji_map = {'1️⃣': 0, '2️⃣': 1, '3️⃣': 2}
        selected_index = emoji_map[reaction.emoji.name]
        
        if selected_index >= len(suggestions_data['titles']):
            return
        
        selected_title = suggestions_data['titles'][selected_index]
        processing_msg = await channel.send(f"🔄 「{selected_title}」の下書きを生成中...")
        
        outline = ai_suggester.generate_article_outline(selected_title)
        full_article = f"# {selected_title}\n\n{outline}"
        
        hatena_api = HatenaBlogAPI(
            hatena_id=config.hatena_id,
            blog_id=config.hatena_blog_id,
            api_key=config.hatena_api_key
        )
        
        result = hatena_api.post_article(
            title=selected_title,
            content=full_article,
            categories=["ブログ", "Tech"],
            draft=True
        )
        
        await processing_msg.delete()
        
        if result['success']:
            embed = discord.Embed(
                title="✅ 下書き投稿が完了しました",
                description=f"記事「{selected_title}」を下書きとして保存しました。",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="📝 記事URL",
                value=f"[編集画面で確認]({result['article_url']})",
                inline=False
            )
            
            embed.add_field(
                name="💡 次のステップ",
                value="はてなブログの管理画面から下書きを確認し、各セクションの内容を執筆してください。",
                inline=False
            )
            
            embed.set_footer(text="RSS Checker Bot")
            await channel.send(embed=embed)
            logger.info(f"✓ Draft article created: {selected_title}")
        else:
            await channel.send(f"❌ エラー: 下書きの作成に失敗しました。\n{result.get('error', 'Unknown error')}")
            logger.error(f"Failed to create draft: {result}")
            
    except Exception as e:
        logger.error(f"Error handling reaction: {e}", exc_info=True)
        try:
            await channel.send(f"❌ エラーが発生しました: {str(e)}")
        except:
            pass

@bot.tree.context_menu(name="ブログ更新状況をチェック")
async def check_blog_context(interaction: discord.Interaction, message: discord.Message):
    """Context menu command to check blog status"""
    await interaction.response.defer(ephemeral=True)
    
    try:
        should_notify, feed_info = rss_checker.should_notify(config.threshold_days)
        
        if not feed_info['success']:
            await interaction.followup.send(f"❌ エラー: {feed_info['error']}", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="📊 ブログ更新状況",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="📝 最新記事",
            value=f"[{feed_info['latest_post_title']}]({feed_info['latest_post_link']})",
            inline=False
        )
        
        embed.add_field(
            name="📅 最終更新",
            value=feed_info['last_updated'].strftime("%Y年%m月%d日 %H:%M"),
            inline=True
        )
        
        embed.add_field(
            name="⏱️ 経過日数",
            value=f"{feed_info['days_since_update']}日",
            inline=True
        )
        
        if should_notify:
            embed.add_field(
                name="⚠️ 状態",
                value="更新が必要です！",
                inline=False
            )
            embed.color = discord.Color.orange()
        else:
            embed.add_field(
                name="✅ 状態",
                value="問題ありません",
                inline=False
            )
            embed.color = discord.Color.green()
        
        embed.set_footer(text="RSS Checker")
        
        await interaction.followup.send(embed=embed, ephemeral=True)
        
    except Exception as e:
        logger.error(f"Error in check_blog_context: {e}")
        await interaction.followup.send(f"❌ エラーが発生しました: {str(e)}", ephemeral=True)


@bot.tree.context_menu(name="AIにテーマ提案してもらう")
async def suggest_theme_context(interaction: discord.Interaction, message: discord.Message):
    """Context menu command to get AI suggestions"""
    await interaction.response.defer(ephemeral=True)
    
    if not ai_suggester:
        await interaction.followup.send("❌ AI機能が設定されていません。Gemini APIキーを設定してください。", ephemeral=True)
        return
    
    try:
        # Get recent blog posts for context
        feed_info = rss_checker.check_feed()
        recent_topics = None
        
        if feed_info['success']:
            recent_topics = [feed_info['latest_post_title']]
        
        # Generate suggestions
        suggestions = ai_suggester.suggest_topics(count=3, recent_topics=recent_topics)
        
        embed = discord.Embed(
            title="🤖 AIによるブログテーマ提案",
            description=suggestions,
            color=discord.Color.purple(),
            timestamp=datetime.utcnow()
        )
        
        embed.set_footer(text="Powered by Google Gemini AI")
        
        await interaction.followup.send(embed=embed, ephemeral=True)
        
    except Exception as e:
        logger.error(f"Error in suggest_theme_context: {e}")
        await interaction.followup.send(f"❌ エラーが発生しました: {str(e)}", ephemeral=True)


@bot.tree.command(name="blog_check", description="ブログの更新状況を今すぐチェック")
async def blog_check(interaction: discord.Interaction):
    """Check blog update status now"""
    await interaction.response.defer()
    
    try:
        should_notify, feed_info = rss_checker.should_notify(config.threshold_days)
        
        if not feed_info['success']:
            await interaction.followup.send(f"❌ エラー: {feed_info['error']}")
            return
        
        embed = discord.Embed(
            title="📊 ブログ更新状況",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="📝 最新記事",
            value=f"[{feed_info['latest_post_title']}]({feed_info['latest_post_link']})",
            inline=False
        )
        
        embed.add_field(
            name="📅 最終更新",
            value=feed_info['last_updated'].strftime("%Y年%m月%d日 %H:%M"),
            inline=True
        )
        
        embed.add_field(
            name="⏱️ 経過日数",
            value=f"{feed_info['days_since_update']}日",
            inline=True
        )
        
        embed.add_field(
            name="🎯 しきい値",
            value=f"{config.threshold_days}日",
            inline=True
        )
        
        if should_notify:
            embed.add_field(
                name="⚠️ 状態",
                value="更新が必要です！",
                inline=False
            )
            embed.color = discord.Color.orange()
        else:
            embed.add_field(
                name="✅ 状態",
                value="問題ありません",
                inline=False
            )
            embed.color = discord.Color.green()
        
        embed.set_footer(text="RSS Checker")
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        logger.error(f"Error in blog_check command: {e}")
        await interaction.followup.send(f"❌ エラーが発生しました: {str(e)}")


@bot.tree.command(name="blog_suggest", description="AIにブログのテーマを提案してもらう")
async def blog_suggest(interaction: discord.Interaction, theme: str = None):
    """Get AI-powered blog topic suggestions"""
    # Respond immediately to avoid timeout
    await interaction.response.send_message("🤖 AIがブログテーマを考えています...", ephemeral=False)
    
    if not ai_suggester:
        await interaction.channel.send("❌ AI機能が設定されていません。Gemini APIキーを設定してください。")
        return
    
    try:
        # Get recent blog posts for context
        feed_info = rss_checker.check_feed()
        recent_topics = None
        
        if feed_info['success']:
            # In a real implementation, you'd get multiple recent posts
            recent_topics = [feed_info['latest_post_title']]
        
        # Generate suggestions
        if theme:
            suggestions = ai_suggester.suggest_with_theme(theme)
            title = f"🤖 AIによるブログテーマ提案（テーマ: {theme}）"
        else:
            suggestions = ai_suggester.suggest_topics(count=3, recent_topics=recent_topics)
            title = "🤖 AIによるブログテーマ提案"
        
        embed = discord.Embed(
            title=title,
            description=suggestions,
            color=discord.Color.purple(),
            timestamp=datetime.utcnow()
        )
        
        embed.set_footer(text="Powered by Google Gemini AI")
        
        # Send as a regular message (not interaction response) so reactions work properly
        message = await interaction.channel.send(embed=embed)
        logger.info(f"Embed sent as regular message, ID: {message.id}")
        
        # Extract titles and add reactions
        try:
            # Debug: Log the raw suggestions
            logger.info(f"Raw suggestions text:\n{suggestions}")
            
            titles = []
            for sline in suggestions.split('\n'):
                # Try multiple patterns
                # Pattern 1: "1. **Title**" or "1. Title"
                match = re.search(r'^\s*\d+\.\s*(?:\*\*)?(.+?)(?:\*\*)?(?:\s*-|$)', sline)
                if not match:
                    # Pattern 2: "### 1. Title"
                    match = re.search(r'^\s*###\s*\d+\.\s*(.+?)(?:\s*$)', sline)
                if not match:
                    # Pattern 3: Just "**Title**" after number
                    match = re.search(r'^\s*\*\*([^*]+)\*\*', sline)
                
                if match:
                    title = match.group(1).strip()
                    # Skip very short matches (likely not titles)
                    if len(title) > 5 and not title.startswith('概要'):
                        titles.append(title)
            
            logger.info(f"Extracted {len(titles)} titles: {titles}")
            
            if titles:
                logger.info(f"Adding reactions to message {message.id}")
                for i, emoji in enumerate(['1️⃣', '2️⃣', '3️⃣'][:len(titles)]):
                    await message.add_reaction(emoji)
                    logger.info(f"Added reaction {i+1}: {emoji}")
                suggestion_messages[message.id] = {'titles': titles, 'timestamp': datetime.utcnow()}
                logger.info(f"✓ Added {len(titles)} reactions to suggestion message")
            else:
                logger.warning(f"No titles extracted from suggestions")
        except Exception as e:
            logger.error(f"Error adding reactions: {e}", exc_info=True)
        
    except Exception as e:
        logger.error(f"Error in blog_suggest command: {e}", exc_info=True)
        await interaction.channel.send(f"❌ エラーが発生しました: {str(e)}")


@bot.tree.command(name="blog_status", description="Bot とRSSチェッカーの状態を表示")
async def blog_status(interaction: discord.Interaction):
    """Show bot status"""
    await interaction.response.defer()
    
    try:
        embed = discord.Embed(
            title="🤖 RSS Checker ステータス",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="📝 監視中のブログ",
            value=config.blog_url,
            inline=False
        )
        
        embed.add_field(
            name="⏰ チェック時刻",
            value=f"毎日 {config.notification_time}",
            inline=True
        )
        
        embed.add_field(
            name="🎯 通知しきい値",
            value=f"{config.threshold_days}日",
            inline=True
        )
        
        embed.add_field(
            name="🧠 AI機能",
            value="有効" if config.gemini_api_key else "無効",
            inline=True
        )
        
        embed.add_field(
            name="🔗 サーバー数",
            value=f"{len(bot.guilds)}",
            inline=True
        )
        
        embed.add_field(
            name="⚡ Ping",
            value=f"{round(bot.latency * 1000)}ms",
            inline=True
        )
        
        embed.set_footer(text="RSS Checker Bot")
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        logger.error(f"Error in blog_status command: {e}")
        await interaction.followup.send(f"❌ エラーが発生しました: {str(e)}")


@tasks.loop(minutes=1)
async def scheduled_check():
    """Scheduled RSS check task"""
    now = datetime.now()
    target_time = datetime.strptime(config.notification_time, "%H:%M").time()
    
    # Check if it's the scheduled time (within the same minute)
    if now.hour == target_time.hour and now.minute == target_time.minute:
        logger.info("⏰ Scheduled check triggered")
        
        try:
            should_notify, feed_info = rss_checker.should_notify(config.threshold_days)
            
            if not feed_info['success']:
                logger.error(f"RSS check failed: {feed_info['error']}")
                return
            
            logger.info(f"Latest post: '{feed_info['latest_post_title']}' ({feed_info['days_since_update']} days ago)")
            
            if feed_info["days_since_update"] >= config.threshold_days:
                logger.warning(f"Threshold exceeded! Sending notification...")
                
                # Get channel
                channel = bot.get_channel(int(config.discord_channel_id))
                if not channel:
                    logger.error(f"Channel {config.discord_channel_id} not found")
                    return
                
                # Create embed
                embed = discord.Embed(
                    title="⚠️ ブログ更新リマインダー",
                    description=f"ブログが **{feed_info['days_since_update']}日間** 更新されていません！",
                    color=discord.Color.orange() if feed_info['days_since_update'] >= 7 else discord.Color.yellow(),
                    timestamp=datetime.utcnow()
                )
                
                embed.add_field(
                    name="📝 最新記事",
                    value=f"[{feed_info['latest_post_title']}]({feed_info['latest_post_link']})",
                    inline=False
                )
                
                embed.add_field(
                    name="📅 最終更新日",
                    value=feed_info['last_updated'].strftime("%Y年%m月%d日 %H:%M"),
                    inline=True
                )
                
                embed.add_field(
                    name="⏱️ 経過日数",
                    value=f"{feed_info['days_since_update']}日",
                    inline=True
                )
                
                # Add motivational message
                if feed_info['days_since_update'] >= 14:
                    message = "2週間以上更新がありません。そろそろ新しい記事を書きませんか？📖"
                elif feed_info['days_since_update'] >= 7:
                    message = "1週間更新がありません。ネタは思いつきましたか？💡"
                else:
                    message = "更新のタイミングです！"
                
                embed.add_field(
                    name="💬 メッセージ",
                    value=message,
                    inline=False
                )
                
                # Add AI suggestion prompt if enabled
                if ai_suggester:
                    embed.add_field(
                        name="🤖 AIでテーマを提案",
                        value="書くテーマが思いつかない？ `/blog_suggest` でAIに提案してもらいましょう！",
                        inline=False
                    )
                
                embed.set_footer(text="RSS Checker")
                
                # Send with @everyone mention
                await channel.send(content="@everyone", embed=embed)
                logger.info("✓ Notification sent successfully!")
                
            else:
                logger.info("✓ Blog is up to date, no notification needed")
                
        except Exception as e:
            logger.error(f"Error in scheduled check: {e}", exc_info=True)


@scheduled_check.before_loop
async def before_scheduled_check():
    """Wait for bot to be ready"""
    await bot.wait_until_ready()



@bot.tree.command(name="make_md", description="記事の1セクション分の見出しと本文を生成する")
@app_commands.describe(detail="このセクションに書きたい内容の説明")
async def make_md(interaction: discord.Interaction, detail: str):
    """Generate a section (heading + content) for blog article"""
    await interaction.response.defer(thinking=True)
    
    try:
        logger.info(f"/make_md command used: {detail[:50]}...")
        
        # あなたの記事スタイルを学習したプロンプト
        prompt = f"""あなたは技術ブログを書くライターである。以下の口調・文体の特徴を厳密に守って記事を書くこと:

【口調の特徴】
- 敬語は使わない（である調、だ調）
- カジュアルで砕けた表現（「〜らしい」「〜みたいな」「〜的な」「というわけで」）
- ユーモアを交えた軽い表現も可（「でございます」など）
- 余計な前置きや挨拶は一切なし
- 端的で分かりやすい説明

【文体の例】
「なんですべての領域を使わないのか？」
「Geminiさんいわく。」
「というわけで、ディスク領域を拡張する方法2パターン+αを紹介。」
「さらなる拡張のためのスペースを確保しようとする　みたいなことが書かれていた。」
「というわけで、初期設定で実ディスク容量（32GB）の一部を拡張しないと使えない領域とされるわけでございます。」

【重要】
- 見出し(###で始まる)と本文のみを出力すること
- 「以下のような〜」「それでは〜」などの前置きは不要
- コードブロックは使わない（Markdown形式そのままで出力）
- 見出しは1つ、その下に本文を記述

【要求内容】
{detail}

上記の内容で、見出し(### )1つと、その下に本文を記述せよ。"""

        response = ai_suggester.model.generate_content(prompt)
        section_content = response.text.strip()
        
        # Markdown形式で返信（コードブロックなし）
        await interaction.followup.send(section_content)
        logger.info("✓ Section generated successfully")
        
    except Exception as e:
        logger.error(f"Error in make_md: {e}", exc_info=True)
        await interaction.followup.send(f"エラーが発生した: {str(e)}")


@bot.tree.command(name="make_sentence", description="質問に対して端的に回答する")
@app_commands.describe(detail="質問内容や説明してほしいこと")
async def make_sentence(interaction: discord.Interaction, detail: str):
    """Answer questions in casual style"""
    await interaction.response.defer(thinking=True)
    
    try:
        logger.info(f"/make_sentence command used: {detail[:50]}...")
        
        # あなたの記事スタイルで質問に回答
        prompt = f"""あなたは技術に詳しいエンジニアである。以下の口調・文体の特徴を厳密に守って質問に回答すること:

【口調の特徴】
- 敬語は使わない（である調、だ調）
- カジュアルで砕けた表現（「〜らしい」「〜みたいな」「〜的な」「というわけで」）
- なるべく端的に、必要最小限の説明で
- 余計な前置きや挨拶は一切なし
- コードや技術用語は適切に使う

【文体の例】
「AIに聞いたらこんな記事を見つけた。」
「複数のパーティションを1つの論理ボリュームとして扱うものらしい。」
「てきなことを言ってた。」

【重要】
- embedは使わない、テキストのみで回答
- コードブロック(```)は使わない
- 前置きなしで本題から始める
- 端的に、必要十分な説明のみ

【質問内容】
{detail}

上記の質問に対して、端的に回答せよ。"""

        response = ai_suggester.model.generate_content(prompt)
        answer = response.text.strip()
        
        # テキスト形式で返信
        await interaction.followup.send(answer)
        logger.info("✓ Answer generated successfully")
        
    except Exception as e:
        logger.error(f"Error in make_sentence: {e}", exc_info=True)
        await interaction.followup.send(f"エラーが発生した: {str(e)}")


def main():
    """Start the bot"""
    try:
        logger.info("Starting RSS Checker Bot...")
        bot.run(config.discord_bot_token)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise


if __name__ == "__main__":
    main()
