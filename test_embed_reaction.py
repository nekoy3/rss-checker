#!/usr/bin/env python3
"""Simple test to check if we can add reactions to embed messages"""

import discord
from discord import app_commands
import asyncio
import logging
from config import load_config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

config = load_config()

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

@bot.event
async def on_ready():
    logger.info(f'✓ Test bot logged in as {bot.user}')
    try:
        synced = await tree.sync()
        logger.info(f'✓ Synced {len(synced)} command(s)')
    except Exception as e:
        logger.error(f'Failed to sync commands: {e}')

@tree.command(name="test_embed", description="Embedメッセージ+リアクションのテスト")
async def test_embed(interaction: discord.Interaction):
    """Test embed with reactions"""
    await interaction.response.defer()
    
    try:
        logger.info("Creating embed...")
        embed = discord.Embed(
            title="🧪 Embedテスト",
            description="このメッセージにリアクションボタンを追加します",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="テスト項目", value="1️⃣ 項目1\n2️⃣ 項目2\n3️⃣ 項目3", inline=False)
        
        logger.info("Sending embed with wait=True...")
        message = await interaction.followup.send(embed=embed, wait=True)
        
        logger.info(f"Message object: {type(message)}")
        logger.info(f"Message ID: {message.id if hasattr(message, 'id') else 'No ID'}")
        
        logger.info("Adding reactions...")
        reactions = ['1️⃣', '2️⃣', '3️⃣']
        for i, emoji in enumerate(reactions):
            await message.add_reaction(emoji)
            logger.info(f"✓ Added reaction {i+1}: {emoji}")
        
        logger.info("✓ Test completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        await interaction.followup.send(f"エラー: {str(e)}")

bot.run(config.discord_bot_token)
