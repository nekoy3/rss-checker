import discord
import asyncio
import os
from config import load_config

config = load_config()

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f"✓ Test bot logged in as {bot.user}")
    print("\nテスト1: 通常メッセージにリアクション")
    print("テスト2: interaction.response.send_message()にリアクション")
    print("テスト3: interaction.followup.send()にリアクション")
    print("\n/test_reactions コマンドを実行してください")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if message.content == "!test_normal":
        # Test 1: Normal message
        sent_msg = await message.channel.send("📝 通常メッセージのテスト")
        await asyncio.sleep(0.5)
        await sent_msg.add_reaction("1️⃣")
        await sent_msg.add_reaction("2️⃣")
        await sent_msg.add_reaction("3️⃣")
        print("✓ Test 1: Normal message reactions added")

# This would be for slash command testing - we'll check the current implementation instead
print("Test bot ready to check interaction types")
