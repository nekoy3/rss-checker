#!/usr/bin/env python3
"""
AI-powered Blog Topic Suggester using Google Gemini API
"""

import google.generativeai as genai
import logging

logger = logging.getLogger(__name__)

class AISuggester:
    """Suggests blog topics using Google Gemini AI"""
    
    def __init__(self, api_key: str):
        """
        Initialize AI suggester with API key
        
        Args:
            api_key: Google Gemini API key
        """
        if not api_key:
            raise ValueError("Gemini API key is required")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        logger.info("✓ AI Suggester initialized with Gemini 2.5 Flash")
    
    def suggest_topics(self, count: int = 3, recent_topics: list = None) -> str:
        """
        Generate blog topic suggestions
        
        Args:
            count: Number of topics to generate
            recent_topics: List of recent blog post titles to avoid duplication
            
        Returns:
            Generated blog topic suggestions as formatted text
        """
        recent_topics_text = ""
        if recent_topics:
            recent_topics_text = "、".join(recent_topics)
        else:
            recent_topics_text = "なし"
        
        prompt = f"""技術ブログのテーマを{count}つ提案する。以下のフォーマットで出力せよ。

【重要】前置き・挨拶文は一切不要。以下のフォーマットのみを出力すること。

-----------------------
### 1. 記事タイトル
概要：記事の内容説明。必ず「である」「だ」で終わる文章で記述する。
-----------------------
### 2. 記事タイトル
概要：記事の内容説明。必ず「である」「だ」で終わる文章で記述する。
-----------------------
### 3. 記事タイトル
概要：記事の内容説明。必ず「である」「だ」で終わる文章で記述する。
-----------------------

【厳格な制約】
- 「はい」「承知しました」「提案します」などの前置き文は絶対に出力しないこと
- 最初の文字は必ず「-----------------------」で始めること
- 記事タイトルは必ず「### 」で始める（Markdown見出しレベル3）
- 概要は「である」「だ」で終わる断定形のみ使用
- 「〜します」「〜ます」「〜ください」などの丁寧語・敬語は完全禁止
- 絵文字（📝など）も不要
- 「対象読者」などの追加情報も不要

最近の投稿: {recent_topics_text}"""
        
        try:
            logger.info(f"Requesting {count} blog topic suggestions from Gemini AI...")
            response = self.model.generate_content(prompt)
            logger.info("✓ AI suggestions generated successfully")
            return response.text
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            raise
    
    def suggest_with_theme(self, theme: str) -> str:
        """
        Generate blog topic suggestions based on a specific theme
        
        Args:
            theme: The theme/topic to focus on
            
        Returns:
            Generated blog topic suggestions as formatted text
        """
        prompt = f"""「{theme}」に関する技術ブログのテーマを3つ提案する。以下のフォーマットで出力せよ。

【重要】前置き・挨拶文は一切不要。以下のフォーマットのみを出力すること。

-----------------------
### 1. 記事タイトル
概要：記事の内容説明。必ず「である」「だ」で終わる文章で記述する。
-----------------------
### 2. 記事タイトル
概要：記事の内容説明。必ず「である」「だ」で終わる文章で記述する。
-----------------------
### 3. 記事タイトル
概要：記事の内容説明。必ず「である」「だ」で終わる文章で記述する。
-----------------------

【厳格な制約】
- 「はい」「承知しました」「提案します」などの前置き文は絶対に出力しないこと
- 最初の文字は必ず「-----------------------」で始めること
- 記事タイトルは必ず「### 」で始める（Markdown見出しレベル3）
- 概要は「である」「だ」で終わる断定形のみ使用
- 「〜します」「〜ます」「〜ください」などの丁寧語・敬語は完全禁止
- 絵文字（📝など）も不要
- 「対象読者」などの追加情報も不要"""
        
        try:
            logger.info(f"Requesting suggestions for theme: {theme}")
            response = self.model.generate_content(prompt)
            logger.info("✓ Theme-based suggestions generated successfully")
            return response.text
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            raise

    def generate_article_outline(self, title: str) -> str:
        """
        Generate detailed article outline with sections and content hints
        
        Args:
            title: Article title
            
        Returns:
            Markdown formatted article outline
        """
        prompt = f"""記事タイトル「{title}」の詳細なアウトラインを生成せよ。

【出力フォーマット】
以下の形式で必ず出力すること。前置きは一切不要。

[:contents]

## セクション1のタイトル
ここに書くべき内容の概要（2-3文）。具体的な技術要素や手順を示唆する。

## セクション2のタイトル
ここに書くべき内容の概要（2-3文）。実装方法やコード例の方向性を示す。

## セクション3のタイトル
ここに書くべき内容の概要（2-3文）。応用例やベストプラクティスに言及する。

## まとめ
ここに書くべき内容の概要（2-3文）。記事全体の要点と次のアクションを示す。

【厳格な制約】
- 最初は必ず「[:contents]」で始める（はてなブログの目次記法）
- 前置き文は絶対に出力しないこと
- セクションは「## 」で始める（Markdown見出しレベル2）
- 各セクションの下に、そのセクションで書くべき内容のヒントを2-3文で記述
- ヒントは具体的で、執筆の指針となる内容にすること
- 「である調」で記述すること
- 敬語（です・ます調）は禁止
- セクション数は3-5個が適切
- 最後に「まとめ」セクションを必ず含める
- 技術ブログとして実践的で読者に役立つ構成にすること"""
        
        try:
            logger.info(f"Generating article outline for: {title}")
            response = self.model.generate_content(prompt)
            logger.info("✓ Article outline generated successfully")
            return response.text
        except Exception as e:
            logger.error(f"Error generating outline: {e}")
            raise
def main():
    """Test the AI suggester"""
    import sys
    
    # This is just for testing
    api_key = input("Enter your Gemini API key: ")
    
    suggester = AISuggester(api_key)
    
    print("\n=== General Suggestions ===")
    suggestions = suggester.suggest_topics(count=3)
    print(suggestions)
    
    print("\n=== Theme-based Suggestions ===")
    theme_suggestions = suggester.suggest_with_theme("Python")
    print(theme_suggestions)

    def generate_article_review(self, article_text: str) -> str:
        """
        AIが記事をレビューして改善提案を返す
        論理展開の正しさと初心者への分かりやすさを重点的にチェック
        
        Args:
            article_text: レビューする記事本文
            
        Returns:
            レビュー結果（改善提案）
        """
        try:
            logger.info("Generating article review...")
            
            # カスタムプロンプト: 論理展開と分かりやすさを重視
            prompt = f"""以下のブログ記事をレビューして、改善提案を出してください。

# レビュー観点
1. **論理展開の正しさ**
   - 話の流れが自然につながっているか
   - 前提→説明→結論の流れが矛盾していないか
   - 因果関係が正しく説明されているか
   - 飛躍した論理や説明不足がないか

2. **初心者への分かりやすさ**
   - 専門用語を使う際に適切な説明があるか
   - 初めてその技術に触れる人でも理解できる表現か
   - 具体例やたとえ話が効果的に使われているか
   - 段階的に理解を深められる構成になっているか

3. **その他の改善点**
   - タイトルの魅力度
   - 見出し構成の適切さ
   - コード例の分かりやすさ（もしあれば）

# 記事本文
{article_text}

# レビュー結果
上記の観点から、具体的な改善提案を箇条書きで教えてください。
良い点も1-2個挙げてモチベーションを保ってください。
改善提案は優先度の高い順に並べてください。"""

            model = genai.GenerativeModel(
                model_name="gemini-2.0-flash-exp",
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 2048,
                }
            )
            
            response = model.generate_content(prompt)
            review_result = response.text.strip()
            
            logger.info("✓ Article review generated successfully")
            return review_result
            
        except Exception as e:
            logger.error(f"✗ Failed to generate article review: {e}")
            return f"エラーが発生しました: {str(e)}"

    def generate_tags_from_content(self, title: str, content: str) -> list:
        """
        記事の内容からSEOに適したタグを自動生成
        
        Args:
            title: 記事タイトル
            content: 記事本文
            
        Returns:
            タグのリスト（5-10個）
        """
        try:
            logger.info(f"Generating tags for article: {title}")
            
            # 記事が長すぎる場合は最初の2000文字だけ使用
            content_snippet = content[:2000] if len(content) > 2000 else content
            
            prompt = f"""以下のブログ記事に最適なタグを5~10個提案してください。

# タグ生成の基準
- はてなブログでよく使われるタグを優先
- 技術系の記事の場合、具体的な技術名（Python、Discord、APIなど）
- 記事のテーマを表すキーワード
- SEO効果が高そうなキーワード
- 抽象的すぎず、具体的すぎないバランスの良いタグ

# 記事タイトル
{title}

# 記事本文（抜粋）
{content_snippet}

# 出力形式
タグをカンマ区切りで出力してください。余計な説明は不要です。
例: Python, Discord Bot, API連携, 自動化, プログラミング, 技術解説"""

            model = genai.GenerativeModel(
                model_name="gemini-2.0-flash-exp",
                generation_config={
                    "temperature": 0.5,
                    "top_p": 0.9,
                    "top_k": 30,
                    "max_output_tokens": 200,
                }
            )
            
            response = model.generate_content(prompt)
            tags_text = response.text.strip()
            
            # カンマ区切りでタグを分割してクリーンアップ
            tags = [tag.strip() for tag in tags_text.split(',')]
            tags = [tag for tag in tags if tag]  # 空文字を除外
            
            logger.info(f"✓ Generated {len(tags)} tags")
            return tags[:10]  # 最大10個
            
        except Exception as e:
            logger.error(f"✗ Failed to generate tags: {e}")
            return []

if __name__ == "__main__":
    main()
