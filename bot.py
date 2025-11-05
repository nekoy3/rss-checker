#!/usr/bin/env python3
"""
RSS Checker Discord Bot
Monitors blog RSS and provides interactive commands
"""

import discord
from discord.ext import commands, tasks
from discord import app_commands
import logging
from datetime import datetime, time as dt_time
import asyncio

from config import load_config
from rss_checker import RSSChecker
from ai_suggester import AISuggester

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
    await interaction.response.defer()
    
    if not ai_suggester:
        await interaction.followup.send("❌ AI機能が設定されていません。Gemini APIキーを設定してください。")
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
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        logger.error(f"Error in blog_suggest command: {e}")
        await interaction.followup.send(f"❌ エラーが発生しました: {str(e)}")


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
