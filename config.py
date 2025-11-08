"""
Configuration reader for RSS Checker
Reads settings from rss.conf file
"""

import configparser
import os
from pathlib import Path
from typing import Optional


class Config:
    """Configuration manager for RSS Checker"""
    
    def __init__(self, config_file: str = "rss.conf"):
        """
        Initialize configuration reader
        
        Args:
            config_file: Path to configuration file (default: rss.conf)
        """
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        
        if not os.path.exists(config_file):
            raise FileNotFoundError(
                f"Configuration file '{config_file}' not found. "
                f"Please copy 'rss.conf.example' to 'rss.conf' and configure it."
            )
        
        self.config.read(config_file)
    
    # Blog settings
    @property
    def blog_url(self) -> str:
        """Get blog URL"""
        return self.config.get("blog", "url")
    
    @property
    def rss_feed_url(self) -> Optional[str]:
        """Get RSS feed URL (optional, may fall back to blog_url)"""
        try:
            return self.config.get("blog", "rss_feed_url")
        except (configparser.NoOptionError, configparser.NoSectionError):
            return None
    
    # Discord settings
    @property
    def discord_bot_token(self) -> Optional[str]:
        """Get Discord bot token (for future bot features)"""
        try:
            token = self.config.get("discord", "bot_token")
            return token if token != "YOUR_BOT_TOKEN_HERE" else None
        except (configparser.NoOptionError, configparser.NoSectionError):
            return None
    
    @property
    def discord_channel_id(self) -> Optional[str]:
        """Get Discord channel ID"""
        try:
            return self.config.get("discord", "channel_id")
        except (configparser.NoOptionError, configparser.NoSectionError):
            return None
    
    @property
    def discord_webhook_url(self) -> Optional[str]:
        """Get Discord webhook URL (alternative to bot)"""
        try:
            return self.config.get("discord", "webhook_url")
        except (configparser.NoOptionError, configparser.NoSectionError):
            return None
    
    # Notification settings
    @property
    def threshold_days(self) -> int:
        """Get notification threshold in days"""
        return self.config.getint("notification", "threshold_days")
    
    @property
    def notification_time(self) -> str:
        """Get notification time (HH:MM format)"""
        return self.config.get("notification", "notification_time")
    
    # AI settings (for future use)
    @property
    def gemini_api_key(self) -> Optional[str]:
        """Get Google Gemini API key (for future AI features)"""
        try:
            key = self.config.get("ai", "gemini_api_key")
            return key if key != "YOUR_GEMINI_API_KEY_HERE" else None
        except (configparser.NoOptionError, configparser.NoSectionError):
            return None
    
    # Blog API settings (for future use)
    @property
    def blog_api_url(self) -> Optional[str]:
        """Get blog API URL (for future posting features)"""
        try:
            return self.config.get("blog_api", "api_url")
        except (configparser.NoOptionError, configparser.NoSectionError):
            return None
    
    @property
    def blog_api_user(self) -> Optional[str]:
        """Get blog API username"""
        try:
            return self.config.get("blog_api", "api_user")
        except (configparser.NoOptionError, configparser.NoSectionError):
            return None
    
    @property
    def blog_api_password(self) -> Optional[str]:
        """Get blog API password"""
        try:
            return self.config.get("blog_api", "api_password")
        except (configparser.NoOptionError, configparser.NoSectionError):
            return None
    

    # Hatena Blog settings
    @property
    def hatena_api_key(self) -> Optional[str]:
        """Get Hatena Blog API key"""
        try:
            return self.config.get("blog", "api_key")
        except (configparser.NoOptionError, configparser.NoSectionError):
            return None
    
    @property
    def hatena_id(self) -> Optional[str]:
        """Extract Hatena ID from blog URL"""
        import re
        url = self.blog_url
        # Extract from https://USERNAME.hateblo.jp/ or https://USERNAME.hatenablog.com/
        match = re.search(r'https?://([^.]+)\.hateblo\.jp', url)
        if not match:
            match = re.search(r'https?://([^.]+)\.hatenablog\.com', url)
        return match.group(1) if match else None
    
    @property
    def hatena_blog_id(self) -> Optional[str]:
        """Extract Hatena Blog ID from blog URL"""
        import re
        url = self.blog_url
        # Extract full domain like nekoy3.hateblo.jp
        match = re.search(r'https?://([^/]+)', url)
        return match.group(1) if match else None
    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate configuration
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required fields
        try:
            if not self.blog_url:
                errors.append("Blog URL is required")
        except Exception as e:
            errors.append(f"Blog URL error: {e}")
        
        try:
            if not self.discord_webhook_url and not self.discord_bot_token:
                errors.append(
                    "Either Discord webhook URL or bot token is required"
                )
        except Exception as e:
            errors.append(f"Discord configuration error: {e}")
        
        try:
            if self.threshold_days < 1:
                errors.append("Threshold days must be at least 1")
        except Exception as e:
            errors.append(f"Threshold days error: {e}")
        
        return (len(errors) == 0, errors)


def load_config(config_file: str = "rss.conf") -> Config:
    """
    Load and validate configuration
    
    Args:
        config_file: Path to configuration file
        
    Returns:
        Config object
        
    Raises:
        ValueError: If configuration is invalid
    """
    config = Config(config_file)
    is_valid, errors = config.validate()
    
    if not is_valid:
        raise ValueError(
            "Invalid configuration:\n" + "\n".join(f"  - {err}" for err in errors)
        )
    
    return config


if __name__ == "__main__":
    # Test configuration loading
    try:
        config = load_config()
        print("✓ Configuration loaded successfully!")
        print(f"  Blog URL: {config.blog_url}")
        print(f"  RSS Feed URL: {config.rss_feed_url or 'Not set'}")
        print(f"  Threshold: {config.threshold_days} days")
        print(f"  Notification time: {config.notification_time}")
        print(f"  Discord webhook: {'Set' if config.discord_webhook_url else 'Not set'}")
        print(f"  Discord bot token: {'Set' if config.discord_bot_token else 'Not set'}")
        print(f"  Gemini API key: {'Set' if config.gemini_api_key else 'Not set'}")
    except Exception as e:
        print(f"✗ Configuration error: {e}")
