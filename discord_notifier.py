"""
Discord Notifier Module
Sends notifications to Discord via Webhook or Bot
"""

import requests
import logging
from typing import Optional, Dict, Any
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DiscordNotifier:
    """Discord notification sender supporting Webhook and Bot methods"""
    
    def __init__(self, webhook_url: Optional[str] = None, bot_token: Optional[str] = None, 
                 channel_id: Optional[str] = None):
        """
        Initialize Discord notifier
        
        Args:
            webhook_url: Discord webhook URL (simple method)
            bot_token: Discord bot token (advanced method, for future features)
            channel_id: Discord channel ID (used with bot token)
        """
        self.webhook_url = webhook_url
        self.bot_token = bot_token
        self.channel_id = channel_id
        
        # Determine which method to use
        self.use_webhook = webhook_url is not None
        self.use_bot = bot_token is not None and channel_id is not None
        
        if not self.use_webhook and not self.use_bot:
            raise ValueError("Either webhook_url or (bot_token + channel_id) must be provided")
    
    def send_notification(self, feed_info: Dict[str, Any]) -> bool:
        """
        Send notification about blog update status
        
        Args:
            feed_info: Dictionary containing feed information from RSSChecker
            
        Returns:
            True if notification sent successfully, False otherwise
        """
        if not feed_info.get('success'):
            logger.error("Cannot send notification: feed check failed")
            return False
        
        # Create message
        embed = self._create_embed(feed_info)
        
        # Send via appropriate method
        if self.use_webhook:
            return self._send_via_webhook(embed)
        elif self.use_bot:
            return self._send_via_bot(embed)
        
        return False
    
    def _create_embed(self, feed_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create Discord embed message
        
        Args:
            feed_info: Feed information dictionary
            
        Returns:
            Discord embed dictionary
        """
        days_since = feed_info['days_since_update']
        last_updated = feed_info['last_updated']
        title = feed_info['latest_post_title']
        link = feed_info['latest_post_link']
        
        # Choose color based on days since update
        if days_since >= 14:
            color = 0xFF0000  # Red - Very overdue
        elif days_since >= 7:
            color = 0xFF9900  # Orange - Overdue
        else:
            color = 0xFFFF00  # Yellow - Warning
        
        embed = {
            "title": "⚠️ ブログ更新リマインダー",
            "description": f"ブログが **{days_since}日間** 更新されていません！",
            "color": color,
            "fields": [
                {
                    "name": "📝 最新記事",
                    "value": f"[{title}]({link})",
                    "inline": False
                },
                {
                    "name": "📅 最終更新日",
                    "value": last_updated.strftime("%Y年%m月%d日 %H:%M"),
                    "inline": True
                },
                {
                    "name": "⏱️ 経過日数",
                    "value": f"{days_since}日",
                    "inline": True
                }
            ],
            "footer": {
                "text": "RSS Checker"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add motivational message based on days
        if days_since >= 14:
            embed["fields"].append({
                "name": "💬 メッセージ",
                "value": "2週間以上更新がありません。そろそろ新しい記事を書きませんか？📖",
                "inline": False
            })
        elif days_since >= 7:
            embed["fields"].append({
                "name": "💬 メッセージ",
                "value": "1週間更新がありません。ネタは思いつきましたか？💡",
                "inline": False
            })
        
        return embed
    
    def _send_via_webhook(self, embed: Dict[str, Any]) -> bool:
        """
        Send notification via Discord webhook
        
        Args:
            embed: Discord embed dictionary
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            logger.info("Sending notification via webhook...")
            
            payload = {
                "embeds": [embed]
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 204:
                logger.info("✓ Notification sent successfully via webhook")
                return True
            else:
                logger.error(f"✗ Webhook request failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Error sending webhook: {e}")
            return False
    
    def _send_via_bot(self, embed: Dict[str, Any]) -> bool:
        """
        Send notification via Discord bot
        
        Args:
            embed: Discord embed dictionary
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            logger.info("Sending notification via bot...")
            
            url = f"https://discord.com/api/v10/channels/{self.channel_id}/messages"
            headers = {
                "Authorization": f"Bot {self.bot_token}",
                "Content-Type": "application/json"
            }
            payload = {
                "embeds": [embed]
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code in [200, 201]:
                logger.info("✓ Notification sent successfully via bot")
                return True
            else:
                logger.error(f"✗ Bot request failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Error sending via bot: {e}")
            return False
    
    def send_test_message(self) -> bool:
        """
        Send a test message to verify configuration
        
        Returns:
            True if test message sent successfully
        """
        test_embed = {
            "title": "✅ RSS Checker テストメッセージ",
            "description": "Discord通知が正しく設定されています！",
            "color": 0x00FF00,
            "fields": [
                {
                    "name": "状態",
                    "value": "✓ 接続成功",
                    "inline": True
                },
                {
                    "name": "通知方法",
                    "value": "Webhook" if self.use_webhook else "Bot",
                    "inline": True
                }
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if self.use_webhook:
            return self._send_via_webhook(test_embed)
        elif self.use_bot:
            return self._send_via_bot(test_embed)
        
        return False


def main():
    """Test Discord notifier"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python discord_notifier.py <WEBHOOK_URL|BOT_TOKEN> [CHANNEL_ID]")
        print("\nFor webhook: python discord_notifier.py <WEBHOOK_URL>")
        print("For bot: python discord_notifier.py <BOT_TOKEN> <CHANNEL_ID>")
        sys.exit(1)
    
    if len(sys.argv) == 2:
        # Webhook mode
        webhook_url = sys.argv[1]
        notifier = DiscordNotifier(webhook_url=webhook_url)
    else:
        # Bot mode
        bot_token = sys.argv[1]
        channel_id = sys.argv[2]
        notifier = DiscordNotifier(bot_token=bot_token, channel_id=channel_id)
    
    print("Sending test notification...")
    success = notifier.send_test_message()
    
    if success:
        print("✓ Test notification sent successfully!")
    else:
        print("✗ Failed to send test notification")
        sys.exit(1)


if __name__ == "__main__":
    main()
