#!/usr/bin/env python3
"""
RSS Checker - Main Script
Monitors blog RSS feed and sends Discord notifications
"""

import logging
import schedule
import time
from datetime import datetime
import argparse

from config import load_config
from rss_checker import RSSChecker
from discord_notifier import DiscordNotifier

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_and_notify():
    """Main check and notify function"""
    try:
        # Load configuration
        logger.info("Loading configuration...")
        config = load_config()
        
        # Determine RSS feed URL
        feed_url = config.rss_feed_url or config.blog_url
        logger.info(f"Checking RSS feed: {feed_url}")
        
        # Check RSS feed
        checker = RSSChecker(feed_url)
        should_notify, feed_info = checker.should_notify(config.threshold_days)
        
        if not feed_info['success']:
            logger.error(f"RSS check failed: {feed_info['error']}")
            return
        
        # Display results
        logger.info(f"Latest post: '{feed_info['latest_post_title']}'")
        logger.info(f"Days since update: {feed_info['days_since_update']}")
        logger.info(f"Threshold: {config.threshold_days} days")
        
        # Send notification if needed
        if should_notify:
            logger.warning(f"Threshold exceeded! Sending notification...")
            
            # Initialize notifier
            notifier = DiscordNotifier(
                webhook_url=config.discord_webhook_url,
                bot_token=config.discord_bot_token,
                channel_id=config.discord_channel_id
            )
            
            # Send notification
            success = notifier.send_notification(feed_info)
            
            if success:
                logger.info("✓ Notification sent successfully!")
            else:
                logger.error("✗ Failed to send notification")
        else:
            logger.info("✓ Blog is up to date, no notification needed")
            
    except Exception as e:
        logger.error(f"Error in check_and_notify: {e}", exc_info=True)


def run_once():
    """Run check once and exit"""
    logger.info("="*60)
    logger.info("RSS Checker - Single Run Mode")
    logger.info("="*60)
    check_and_notify()
    logger.info("="*60)


def run_scheduled():
    """Run check on schedule"""
    try:
        # Load config to get notification time
        config = load_config()
        notification_time = config.notification_time
        
        logger.info("="*60)
        logger.info("RSS Checker - Scheduled Mode")
        logger.info(f"Scheduled time: {notification_time} daily")
        logger.info("="*60)
        
        # Schedule the check
        schedule.every().day.at(notification_time).do(check_and_notify)
        
        logger.info(f"Waiting for scheduled time ({notification_time})...")
        logger.info("Press Ctrl+C to stop")
        
        # Run scheduler
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
            
    except KeyboardInterrupt:
        logger.info("\n\nScheduler stopped by user")
    except Exception as e:
        logger.error(f"Error in scheduler: {e}", exc_info=True)


def test_config():
    """Test configuration and connections"""
    logger.info("="*60)
    logger.info("RSS Checker - Configuration Test")
    logger.info("="*60)
    
    try:
        # Load and validate config
        logger.info("1. Loading configuration...")
        config = load_config()
        logger.info("   ✓ Configuration loaded successfully")
        
        # Display config
        logger.info("\n2. Configuration details:")
        logger.info(f"   Blog URL: {config.blog_url}")
        logger.info(f"   RSS Feed URL: {config.rss_feed_url or 'Using blog URL'}")
        logger.info(f"   Threshold: {config.threshold_days} days")
        logger.info(f"   Notification time: {config.notification_time}")
        logger.info(f"   Discord method: {'Webhook' if config.discord_webhook_url else 'Bot'}")
        logger.info(f"   Gemini API: {'Configured' if config.gemini_api_key else 'Not configured'}")
        
        # Test RSS feed
        logger.info("\n3. Testing RSS feed...")
        feed_url = config.rss_feed_url or config.blog_url
        checker = RSSChecker(feed_url)
        feed_info = checker.check_feed()
        
        if feed_info['success']:
            logger.info("   ✓ RSS feed accessible")
            logger.info(f"   Latest post: {feed_info['latest_post_title']}")
            logger.info(f"   Published: {feed_info['last_updated']}")
            logger.info(f"   Days ago: {feed_info['days_since_update']}")
        else:
            logger.error(f"   ✗ RSS feed error: {feed_info['error']}")
        
        # Test Discord
        logger.info("\n4. Testing Discord notification...")
        notifier = DiscordNotifier(
            webhook_url=config.discord_webhook_url,
            bot_token=config.discord_bot_token,
            channel_id=config.discord_channel_id
        )
        
        if notifier.send_test_message():
            logger.info("   ✓ Discord notification working")
        else:
            logger.error("   ✗ Discord notification failed")
        
        logger.info("\n" + "="*60)
        logger.info("✓ Configuration test complete!")
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"\n✗ Configuration test failed: {e}")
        logger.info("="*60)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='RSS Checker - Monitor blog updates and notify via Discord'
    )
    parser.add_argument(
        '--mode', '-m',
        choices=['once', 'schedule', 'test'],
        default='once',
        help='Run mode: once (single check), schedule (daily at set time), test (config test)'
    )
    
    args = parser.parse_args()
    
    if args.mode == 'once':
        run_once()
    elif args.mode == 'schedule':
        run_scheduled()
    elif args.mode == 'test':
        test_config()


if __name__ == "__main__":
    main()
