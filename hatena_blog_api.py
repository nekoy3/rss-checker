#!/usr/bin/env python3
"""
Hatena Blog API Client (AtomPub)
Provides methods to post, update, and manage blog articles
"""

import hashlib
import base64
import datetime
import requests
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class HatenaBlogAPI:
    """Client for Hatena Blog AtomPub API"""
    
    def __init__(self, hatena_id: str, blog_id: str, api_key: str):
        """
        Initialize Hatena Blog API client
        
        Args:
            hatena_id: Hatena ID (username)
            blog_id: Blog ID (e.g., username.hateblo.jp)
            api_key: API key from Hatena Blog settings
        """
        if not all([hatena_id, blog_id, api_key]):
            raise ValueError("hatena_id, blog_id, and api_key are required")
        
        self.hatena_id = hatena_id
        self.blog_id = blog_id
        self.api_key = api_key
        self.endpoint = f"https://blog.hatena.ne.jp/{hatena_id}/{blog_id}/atom"
        
        logger.info(f"✓ Hatena Blog API initialized for {blog_id}")
    
    def _create_wsse_header(self) -> str:
        """
        Create WSSE authentication header
        
        Returns:
            WSSE header string
        """
        # Create nonce (random string)
        nonce = hashlib.sha1(str(datetime.datetime.now()).encode()).digest()
        nonce_base64 = base64.b64encode(nonce).decode()
        
        # Create created timestamp
        created = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        
        # Create password digest
        # PasswordDigest = Base64(SHA1(Nonce + Created + APIKey))
        digest_source = nonce + created.encode() + self.api_key.encode()
        password_digest = base64.b64encode(hashlib.sha1(digest_source).digest()).decode()
        
        # Create WSSE header
        wsse = (
            f'UsernameToken Username="{self.hatena_id}", '
            f'PasswordDigest="{password_digest}", '
            f'Nonce="{nonce_base64}", '
            f'Created="{created}"'
        )
        
        return wsse
    
    def _create_entry_xml(
        self,
        title: str,
        content: str,
        categories: list = None,
        draft: bool = True
    ) -> str:
        """
        Create Atom entry XML for blog post
        
        Args:
            title: Article title
            content: Article content (Markdown or HTML)
            categories: List of category names
            draft: Whether to post as draft (default: True)
            
        Returns:
            XML string
        """
        import html
        
        # Escape special characters for XML
        title_escaped = html.escape(title)
        content_escaped = html.escape(content)
        
        categories_xml = ""
        if categories:
            for category in categories:
                category_escaped = html.escape(category)
                categories_xml += f'  <category term="{category_escaped}" />\n'
        
        draft_xml = "yes" if draft else "no"
        
        xml = f'''<?xml version="1.0" encoding="utf-8"?>
<entry xmlns="http://www.w3.org/2005/Atom"
       xmlns:app="http://www.w3.org/2007/app">
  <title>{title_escaped}</title>
  <content type="text/x-markdown">{content_escaped}</content>
{categories_xml}  <app:control>
    <app:draft>{draft_xml}</app:draft>
  </app:control>
</entry>'''
        
        return xml
    
    def post_article(
        self,
        title: str,
        content: str,
        categories: list = None,
        draft: bool = True
    ) -> Dict[str, Any]:
        """
        Post a new article to Hatena Blog
        
        Args:
            title: Article title
            content: Article content (Markdown format)
            categories: List of category names
            draft: Whether to post as draft (default: True for safety)
            
        Returns:
            Dict with success status and response data
        """
        try:
            logger.info(f"Posting article: '{title}' (draft={draft})")
            
            # Create XML entry
            entry_xml = self._create_entry_xml(title, content, categories, draft)
            
            # Create headers
            headers = {
                'X-WSSE': self._create_wsse_header(),
                'Content-Type': 'application/xml; charset=utf-8'
            }
            
            # Post to API
            url = f"{self.endpoint}/entry"
            response = requests.post(url, data=entry_xml.encode('utf-8'), headers=headers)
            
            if response.status_code == 201:
                logger.info("✓ Article posted successfully!")
                
                # Parse response to get entry ID for management URL
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.content)
                
                # Get entry ID from response
                ns = {'atom': 'http://www.w3.org/2005/Atom'}
                id_elem = root.find('atom:id', ns)
                
                # Create management URL format: https://blog.hatena.ne.jp/{hatena_id}/{blog_id}/
                article_url = f"https://blog.hatena.ne.jp/{self.hatena_id}/{self.blog_id}/"
                
                return {
                    'success': True,
                    'status_code': response.status_code,
                    'article_url': article_url,
                    'message': 'Article posted successfully'
                }
            else:
                logger.error(f"✗ Failed to post article: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'error': response.text,
                    'message': 'Failed to post article'
                }
                
        except Exception as e:
            logger.error(f"✗ Error posting article: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'message': 'Exception occurred while posting article'
            }
    
    def test_connection(self) -> bool:
        """
        Test API connection by fetching blog entries
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            logger.info("Testing Hatena Blog API connection...")
            
            headers = {
                'X-WSSE': self._create_wsse_header()
            }
            
            url = f"{self.endpoint}/entry"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                logger.info("✓ API connection successful!")
                return True
            else:
                logger.error(f"✗ API connection failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Connection test failed: {e}")
            return False


def main():
    """Test the Hatena Blog API"""
    from config import load_config
    
    # Load configuration
    config = load_config()
    
    # Initialize API client
    api = HatenaBlogAPI(
        hatena_id=config.hatena_id,
        blog_id=config.hatena_blog_id,
        api_key=config.hatena_api_key
    )
    
    # Test connection
    print("\n" + "=" * 60)
    print("Testing Hatena Blog API Connection")
    print("=" * 60)
    
    if api.test_connection():
        print("✓ Connection test passed!\n")
        
        # Test posting a draft article
        print("=" * 60)
        print("Posting test article (draft)")
        print("=" * 60)
        
        result = api.post_article(
            title="[Test] RSS Checker Bot テスト投稿",
            content="""# テスト投稿

これはRSS Checker Botからの自動投稿テストである。

## 機能テスト

- Hatena Blog API (AtomPub)
- WSSE認証
- Markdown形式の投稿

**正常に投稿できている場合、この記事は下書きとして保存されている。**""",
            categories=["テスト", "Bot"],
            draft=True  # Safety: post as draft
        )
        
        print("\n結果:")
        print(f"  成功: {result['success']}")
        print(f"  ステータス: {result.get('status_code', 'N/A')}")
        if result['success']:
            print(f"  記事URL: {result.get('article_url', 'N/A')}")
        else:
            print(f"  エラー: {result.get('error', 'Unknown')}")
    else:
        print("✗ Connection test failed")


if __name__ == "__main__":
    # Set up logging for standalone testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    main()
