#!/usr/bin/env python3
"""
Test different XML formats for Hatena Blog API
"""

import requests
import hashlib
import base64
import datetime
from config import load_config

config = load_config()

def create_wsse_header(hatena_id, api_key):
    """Create WSSE authentication header"""
    nonce = hashlib.sha1(str(datetime.datetime.now()).encode()).digest()
    nonce_base64 = base64.b64encode(nonce).decode()
    created = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    digest_source = nonce + created.encode() + api_key.encode()
    password_digest = base64.b64encode(hashlib.sha1(digest_source).digest()).decode()
    
    wsse = (
        f'UsernameToken Username="{hatena_id}", '
        f'PasswordDigest="{password_digest}", '
        f'Nonce="{nonce_base64}", '
        f'Created="{created}"'
    )
    return wsse

# Test 1: content type only
xml_v1 = '''<?xml version="1.0" encoding="utf-8"?>
<entry xmlns="http://www.w3.org/2005/Atom"
       xmlns:app="http://www.w3.org/2007/app">
  <title>[Test] V1: content type only</title>
  <content type="text/x-markdown"># V1テスト

これは`type="text/x-markdown"`のみを指定したテストである。</content>
  <category term="テスト" />
  <app:control>
    <app:draft>yes</app:draft>
  </app:control>
</entry>'''

# Test 2: Add hatena:syntax
xml_v2 = '''<?xml version="1.0" encoding="utf-8"?>
<entry xmlns="http://www.w3.org/2005/Atom"
       xmlns:app="http://www.w3.org/2007/app"
       xmlns:hatena="http://www.hatena.ne.jp/info/xmlns#">
  <title>[Test] V2: with hatena:syntax</title>
  <content type="text/plain"># V2テスト

これは`hatena:syntax`を指定したテストである。</content>
  <hatena:syntax>markdown</hatena:syntax>
  <category term="テスト" />
  <app:control>
    <app:draft>yes</app:draft>
  </app:control>
</entry>'''

endpoint = f"https://blog.hatena.ne.jp/{config.hatena_id}/{config.hatena_blog_id}/atom/entry"

for version, xml in [("V1", xml_v1), ("V2", xml_v2)]:
    print(f"\n{'='*60}")
    print(f"Testing {version}")
    print(f"{'='*60}")
    
    headers = {
        'X-WSSE': create_wsse_header(config.hatena_id, config.hatena_api_key),
        'Content-Type': 'application/xml; charset=utf-8'
    }
    
    response = requests.post(endpoint, data=xml.encode('utf-8'), headers=headers)
    
    if response.status_code == 201:
        print(f"✓ {version}: 投稿成功")
    else:
        print(f"✗ {version}: 投稿失敗 ({response.status_code})")
        print(f"  Response: {response.text[:200]}")

print(f"\n✓ テスト完了。はてなブログの管理画面で編集モードを確認してください")
print(f"  URL: https://blog.hatena.ne.jp/{config.hatena_id}/{config.hatena_blog_id}/")
