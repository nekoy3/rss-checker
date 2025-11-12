# bot.pyに新しいコマンドを追加
with open('bot.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# main()関数の前に新しいコマンドを挿入
insert_position = None
for i, line in enumerate(lines):
    if line.strip() == 'def main():':
        insert_position = i
        break

if insert_position is None:
    print("Error: Could not find insertion point")
    exit(1)

new_commands = '''
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


'''

# 新しいコマンドを挿入
lines.insert(insert_position, new_commands)

# ファイルに書き戻し
with open('bot.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✓ Added new commands: /make_md and /make_sentence")
print("  - /make_md: Generate blog section (heading + content)")
print("  - /make_sentence: Answer questions in casual style")
print("  - Both commands use your article's tone and style")
