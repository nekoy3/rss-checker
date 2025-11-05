"""
AI Blog Suggester Module
Uses Google Gemini API to suggest blog topics
"""

import logging
from typing import Optional
import google.generativeai as genai

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AISuggester:
    """AI-powered blog topic suggester using Google Gemini"""
    
    def __init__(self, api_key: str):
        """
        Initialize AI suggester
        
        Args:
            api_key: Google Gemini API key
        """
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def suggest_topics(self, count: int = 3, recent_topics: Optional[list] = None) -> str:
        """
        Suggest blog topics
        
        Args:
            count: Number of topics to suggest
            recent_topics: List of recent blog post titles to avoid duplicates
            
        Returns:
            Formatted string with suggested topics
        """
        try:
            logger.info(f"Requesting {count} blog topic suggestions from Gemini AI...")
            
            # Build prompt
            prompt = f"""あなたはブログ記事のテーマを提案するアシスタントです。
技術ブログ向けの面白くて実用的なテーマを{count}つ提案してください。

要件:
- プログラミング、ネットワーク、インフラ、開発ツールなどの技術系トピック
- 初心者から中級者向けの実践的な内容
- 具体的で書きやすいテーマ
- タイトルと簡単な概要（2-3行）を含める

フォーマット:
📝 [タイトル]
概要: [2-3行の説明]
"""
            
            if recent_topics:
                prompt += f"\n\n最近の記事タイトル（これらと重複しないようにしてください）:\n"
                for topic in recent_topics[:5]:
                    prompt += f"- {topic}\n"
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                logger.info("✓ AI suggestions generated successfully")
                return response.text
            else:
                logger.error("AI response was empty")
                return "申し訳ありません。提案を生成できませんでした。"
                
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            return f"エラーが発生しました: {str(e)}"
    
    def suggest_with_theme(self, theme: str) -> str:
        """
        Suggest blog topics based on a specific theme
        
        Args:
            theme: Theme or topic area
            
        Returns:
            Formatted string with suggested topics
        """
        try:
            logger.info(f"Requesting suggestions for theme: {theme}")
            
            prompt = f"""あなたはブログ記事のテーマを提案するアシスタントです。
「{theme}」というテーマに関連する技術ブログ記事のアイデアを3つ提案してください。

要件:
- 具体的で実践的な内容
- 読者が実際に試せるようなハウツー要素を含める
- 初心者から中級者向け
- タイトルと詳細な概要（3-4行）を含める

フォーマット:
📝 [タイトル]
概要: [3-4行の説明]
対象読者: [想定する読者層]
"""
            
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                logger.info("✓ Theme-based suggestions generated successfully")
                return response.text
            else:
                logger.error("AI response was empty")
                return "申し訳ありません。提案を生成できませんでした。"
                
        except Exception as e:
            logger.error(f"Error generating theme suggestions: {e}")
            return f"エラーが発生しました: {str(e)}"


def main():
    """Test AI suggester"""
    import sys
    from config import load_config
    
    try:
        config = load_config()
        
        if not config.gemini_api_key:
            print("✗ Gemini API key not configured")
            sys.exit(1)
        
        suggester = AISuggester(config.gemini_api_key)
        
        print("="*60)
        print("AI Blog Topic Suggester Test")
        print("="*60)
        print("\nGenerating suggestions...\n")
        
        suggestions = suggester.suggest_topics(count=3)
        print(suggestions)
        
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
