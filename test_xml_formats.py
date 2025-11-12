#!/usr/bin/env python3
import requests
from requests.auth import HTTPBasicAuth
import hashlib
import base64
from datetime import datetime
import random
import string

hatena_id = "nekoy3"
hatena_blog_id = "nekoy3.hateblo.jp"
api_key = "dk8998f2au"

def generate_wsse_header(username: str, api_key: str) -> str:
    created = datetime.now().isoformat() + "Z"
    nonce = ''.join(random.choices(string.ascii_letters + string.digits, k=40))
    
    digest_base = nonce + created + api_key
    password_digest = base64.b64encode(
        hashlib.sha1(digest_base.encode()).digest()
    ).decode()
    
    b64nonce = base64.b64encode(nonce.encode()).decode()
    
    return f'UsernameToken Username="{username}", PasswordDigest="{password_digest}", Nonce="{b64nonce}", Created="{created}"'

# Test 1: content type="text/x-markdown"のみ
print("=" * 60)
print("Test 1: content type=\"text/x-markdown\" only")
print("=" * 60)

xml1 = f'''<?xml version="1.0" encoding="utf-8"?>
<entry xmlns="http://www.w3.org/2005/Atom"
       xmlns:app="http://www.w3.org/2007/app">
  <title>[Test1] content type=text/x-markdown</title>
  <content type="text/x-markdown">
# テスト記事1

これは**Markdown**で書かれたテスト記事です。

## セクション1
- リスト項目1
- リスト項目2
  </content>
  <app:control>
    <app:draft>yes</app:draft>
  </app:control>
</entry>'''

headers = {
    "X-WSSE": generate_wsse_header(hatena_id, api_key),
    "Content-Type": "application/xml"
}

response = requests.post(
    f"https://blog.hatena.ne.jp/{hatena_id}/{hatena_blog_id}/atom/entry",
    data=xml1.encode('utf-8'),
    headers=headers
)

print(f"Status: {response.status_code}")
if response.status_code == 201:
    print("✓ Success!")
else:
    print(f"✗ Failed: {response.text}")
print()

# Test 2: hatena:syntax属性を追加
print("=" * 60)
print("Test 2: content + hatena:syntax attribute")
print("=" * 60)

xml2 = f'''<?xml version="1.0" encoding="utf-8"?>
<entry xmlns="http://www.w3.org/2005/Atom"
       xmlns:app="http://www.w3.org/2007/app"
       xmlns:hatena="http://www.hatena.ne.jp/info/xmlns#">
  <title>[Test2] hatena:syntax=markdown</title>
  <hatena:syntax>markdown</hatena:syntax>
  <content type="text/plain">
# テスト記事2

これは**Markdown**で書かれたテスト記事です。

## セクション2
- リスト項目1
- リスト項目2
  </content>
  <app:control>
    <app:draft>yes</app:draft>
  </app:control>
</entry>'''

response = requests.post(
    f"https://blog.hatena.ne.jp/{hatena_id}/{hatena_blog_id}/atom/entry",
    data=xml2.encode('utf-8'),
    headers=headers
)

print(f"Status: {response.status_code}")
if response.status_code == 201:
    print("✓ Success!")
else:
    print(f"✗ Failed: {response.text}")
print()

# Test 3: content type="text/x-hatena-syntax" + hatena:syntax
print("=" * 60)
print("Test 3: content type=text/x-hatena-syntax + hatena:syntax")
print("=" * 60)

xml3 = f'''<?xml version="1.0" encoding="utf-8"?>
<entry xmlns="http://www.w3.org/2005/Atom"
       xmlns:app="http://www.w3.org/2007/app"
       xmlns:hatena="http://www.hatena.ne.jp/info/xmlns#">
  <title>[Test3] text/x-hatena-syntax</title>
  <content type="text/x-hatena-syntax">
# テスト記事3

これは**Markdown**で書かれたテスト記事です。

## セクション3
- リスト項目1
- リスト項目2
  </content>
  <hatena:syntax>markdown</hatena:syntax>
  <app:control>
    <app:draft>yes</app:draft>
  </app:control>
</entry>'''

response = requests.post(
    f"https://blog.hatena.ne.jp/{hatena_id}/{hatena_blog_id}/atom/entry",
    data=xml3.encode('utf-8'),
    headers=headers
)

print(f"Status: {response.status_code}")
if response.status_code == 201:
    print("✓ Success!")
else:
    print(f"✗ Failed: {response.text}")
print()

print("=" * 60)
print("✓ 3つのテスト投稿完了")
print("はてなブログ管理画面で編集モードを確認してください:")
print(f"https://blog.hatena.ne.jp/{hatena_id}/{hatena_blog_id}/")
print("=" * 60)
