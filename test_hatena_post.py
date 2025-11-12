#!/usr/bin/env python3
"""
Test Hatena Blog API posting with different content types
"""

from hatena_blog_api import HatenaBlogAPI
from config import load_config
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

config = load_config()

api = HatenaBlogAPI(
    hatena_id=config.hatena_id,
    blog_id=config.hatena_blog_id,
    api_key=config.hatena_api_key
)

# Test posting with Markdown
print("=" * 60)
print("Testing Markdown mode post")
print("=" * 60)

test_title = "[Test] Markdown編集モードのテスト"
test_content = """# Markdownテスト

これはMarkdown形式のテスト記事である。

## セクション1
- リスト項目1
- リスト項目2

## セクション2
**太字** と *斜体* のテスト

## コードブロック
```python
def hello():
    print("Hello, World!")
```

## まとめ
Markdown形式で正しく投稿できているかを確認する。
"""

result = api.post_article(
    title=test_title,
    content=test_content,
    categories=["テスト", "Markdown"],
    draft=True
)

print(f"\n結果: {'成功' if result['success'] else '失敗'}")
print(f"URL: {result.get('article_url', 'N/A')}")
print(f"\n✓ はてなブログの管理画面で編集モードを確認してください")
print(f"  期待: マークダウン")
print(f"  URL: {result.get('article_url', 'N/A')}")
