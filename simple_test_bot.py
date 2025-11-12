#!/usr/bin/env python3
"""Simple test: Send embed and add reactions on startup"""

import discord
import asyncio
import logging
from config import load_config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

config = load_config()

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    logger.info(f'✓ Bot logged in as {bot.user}')
    
    # Get the first text channel we can send to
    for guild in bot.guilds:
        logger.info(f'Found guild: {guild.name}')
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                logger.info(f'Using channel: {channel.name}')
                
                try:
                    # Test 1: Normal message with reactions
                    logger.info("Test 1: Sending normal message...")
                    msg1 = await channel.send("🧪 **テスト1**: 通常メッセージ")
                    await msg1.add_reaction('1️⃣')
                    await msg1.add_reaction('2️⃣')
                    await msg1.add_reaction('3️⃣')
                    logger.info("✓ Test 1: Normal message reactions added")
                    
                    await asyncio.sleep(1)
                    
                    # Test 2: Embed message with reactions
                    logger.info("Test 2: Sending embed message...")
                    embed = discord.Embed(
                        title="🧪 テスト2: Embedメッセージ",
                        description="このEmbedにリアクションを追加します",
                        color=discord.Color.blue()
                    )
                    embed.add_field(name="項目", value="1️⃣ 項目1\n2️⃣ 項目2\n3️⃣ 項目3", inline=False)
                    
                    msg2 = await channel.send(embed=embed)
                    logger.info(f"Embed sent, message type: {type(msg2)}, ID: {msg2.id}")
                    
                    await msg2.add_reaction('1️⃣')
                    logger.info("✓ Added 1️⃣")
                    await msg2.add_reaction('2️⃣')
                    logger.info("✓ Added 2️⃣")
                    await msg2.add_reaction('3️⃣')
                    logger.info("✓ Added 3️⃣")
                    logger.info("✓ Test 2: Embed message reactions added")
                    
                    await asyncio.sleep(1)
                    
                    # Test 3: Embed with multiple fields
                    logger.info("Test 3: Sending complex embed...")
                    embed3 = discord.Embed(
                        title="🤖 AIによるブログテーマ提案",
                        description="以下のテーマから選択してください",
                        color=discord.Color.purple()
                    )
                    embed3.add_field(
                        name="1. SSH Configでネットワーク機器への接続を爆速化するだ",
                        value="概要：複雑なネットワーク機器へのSSH接続情報をシンプルに管理・接続する方法を解説",
                        inline=False
                    )
                    embed3.add_field(
                        name="2. PythonとParamikoでネットワーク機器の操作を自動化する術",
                        value="概要：SSH経由でネットワーク機器に接続し、コマンドの実行や設定の取得、変更といった操作を自動化",
                        inline=False
                    )
                    embed3.set_footer(text="Powered by Google Gemini AI")
                    
                    msg3 = await channel.send(embed=embed3)
                    logger.info(f"Complex embed sent, message type: {type(msg3)}, ID: {msg3.id}")
                    
                    await msg3.add_reaction('1️⃣')
                    await msg3.add_reaction('2️⃣')
                    logger.info("✓ Test 3: Complex embed reactions added")
                    
                    logger.info("=" * 60)
                    logger.info("✅ All tests completed! Check Discord to see the results.")
                    logger.info("=" * 60)
                    
                except Exception as e:
                    logger.error(f"❌ Error during test: {e}", exc_info=True)
                
                # Close bot after tests
                await asyncio.sleep(2)
                await bot.close()
                return
    
    logger.error("No suitable channel found")
    await bot.close()

bot.run(config.discord_bot_token)
