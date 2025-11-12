#!/usr/bin/env python3
"""Test the new AI functions"""

import logging
from ai_suggester import AISuggester

logging.basicConfig(level=logging.INFO)

# Initialize AI Suggester
ai = AISuggester()

# Test article review
print("=" * 60)
print("Testing Article Review")
print("=" * 60)

test_article = """
# Pythonでファイル操作

Pythonでファイルを読み書きするのは簡単だ。
open()関数を使えばいい。

## 例

file = open('test.txt', 'r')
data = file.read()
file.close()

これでファイルが読める。
"""

review = ai.generate_article_review(test_article)
print(review)
print()

# Test tag generation
print("=" * 60)
print("Testing Tag Generation")
print("=" * 60)

tags = ai.generate_tags_from_content(
    title="Pythonでファイル操作",
    content=test_article
)
print(f"Generated tags: {tags}")
print()

print("✓ All tests passed!")
