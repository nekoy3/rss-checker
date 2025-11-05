"""
RSS Feed Checker Module
Checks blog RSS feed for last update date
"""

import feedparser
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RSSChecker:
    """RSS feed checker for monitoring blog updates"""
    
    def __init__(self, feed_url: str):
        """
        Initialize RSS checker
        
        Args:
            feed_url: URL of the RSS feed to monitor
        """
        self.feed_url = feed_url
        
    def check_feed(self) -> Dict[str, Any]:
        """
        Check RSS feed and return information about latest post
        
        Returns:
            Dictionary containing:
                - success: bool - Whether the check was successful
                - last_updated: datetime - Date of last post (if found)
                - days_since_update: int - Days since last update
                - latest_post_title: str - Title of latest post
                - latest_post_link: str - Link to latest post
                - error: str - Error message (if any)
        """
        result = {
            'success': False,
            'last_updated': None,
            'days_since_update': None,
            'latest_post_title': None,
            'latest_post_link': None,
            'error': None
        }
        
        try:
            logger.info(f"Fetching RSS feed: {self.feed_url}")
            feed = feedparser.parse(self.feed_url)
            
            # Check if feed was parsed successfully
            if feed.bozo:
                # Feed has errors but might still be usable
                logger.warning(f"Feed parsing warning: {feed.bozo_exception}")
            
            # Check if feed has entries
            if not feed.entries:
                result['error'] = "No entries found in RSS feed"
                logger.error(result['error'])
                return result
            
            # Get the latest entry
            latest_entry = feed.entries[0]
            
            # Extract published date
            published_date = self._extract_date(latest_entry)
            
            if not published_date:
                result['error'] = "Could not extract date from latest post"
                logger.error(result['error'])
                return result
            
            # Calculate days since update
            now = datetime.now(timezone.utc)
            days_since = (now - published_date).days
            
            # Fill result
            result['success'] = True
            result['last_updated'] = published_date
            result['days_since_update'] = days_since
            result['latest_post_title'] = latest_entry.get('title', 'No title')
            result['latest_post_link'] = latest_entry.get('link', '')
            
            logger.info(f"Latest post: '{result['latest_post_title']}' ({days_since} days ago)")
            
            return result
            
        except Exception as e:
            result['error'] = f"Error checking RSS feed: {str(e)}"
            logger.error(result['error'])
            return result
    
    def _extract_date(self, entry) -> Optional[datetime]:
        """
        Extract and parse date from RSS entry
        
        Args:
            entry: RSS feed entry
            
        Returns:
            datetime object or None if date could not be extracted
        """
        # Try different date fields
        date_fields = ['published_parsed', 'updated_parsed', 'created_parsed']
        
        for field in date_fields:
            if hasattr(entry, field):
                time_struct = getattr(entry, field)
                if time_struct:
                    try:
                        # Convert time_struct to datetime
                        dt = datetime(*time_struct[:6], tzinfo=timezone.utc)
                        return dt
                    except Exception as e:
                        logger.warning(f"Could not parse {field}: {e}")
                        continue
        
        # If structured date not found, try string dates
        string_fields = ['published', 'updated', 'created']
        for field in string_fields:
            if hasattr(entry, field):
                date_string = getattr(entry, field)
                if date_string:
                    try:
                        from dateutil import parser
                        dt = parser.parse(date_string)
                        # Ensure timezone aware
                        if dt.tzinfo is None:
                            dt = dt.replace(tzinfo=timezone.utc)
                        return dt
                    except Exception as e:
                        logger.warning(f"Could not parse {field} string: {e}")
                        continue
        
        return None
    
    def should_notify(self, threshold_days: int) -> tuple[bool, Dict[str, Any]]:
        """
        Check if notification should be sent based on threshold
        
        Args:
            threshold_days: Number of days without update before notifying
            
        Returns:
            Tuple of (should_notify: bool, feed_info: dict)
        """
        feed_info = self.check_feed()
        
        if not feed_info['success']:
            logger.error(f"Feed check failed: {feed_info['error']}")
            return False, feed_info
        
        days_since = feed_info['days_since_update']
        should_send = days_since >= threshold_days
        
        if should_send:
            logger.warning(f"Threshold exceeded: {days_since} days >= {threshold_days} days")
        else:
            logger.info(f"No notification needed: {days_since} days < {threshold_days} days")
        
        return should_send, feed_info


def main():
    """Test RSS checker"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python rss_checker.py <RSS_FEED_URL> [threshold_days]")
        sys.exit(1)
    
    feed_url = sys.argv[1]
    threshold_days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    
    checker = RSSChecker(feed_url)
    should_notify, info = checker.should_notify(threshold_days)
    
    print(f"\n{'='*60}")
    print(f"RSS Feed Check Results")
    print(f"{'='*60}")
    print(f"Feed URL: {feed_url}")
    print(f"Threshold: {threshold_days} days")
    print(f"{'='*60}")
    
    if info['success']:
        print(f"✓ Latest post: {info['latest_post_title']}")
        print(f"✓ Published: {info['last_updated'].strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"✓ Days since update: {info['days_since_update']}")
        print(f"✓ Link: {info['latest_post_link']}")
        print(f"{'='*60}")
        
        if should_notify:
            print(f"⚠️  NOTIFICATION REQUIRED: Blog hasn't been updated in {info['days_since_update']} days!")
        else:
            print(f"✓ No notification needed (updated {info['days_since_update']} days ago)")
    else:
        print(f"✗ Error: {info['error']}")
    
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
