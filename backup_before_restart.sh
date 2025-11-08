#!/bin/bash
# Backup script - Run before restarting the bot service

BACKUP_DIR="$HOME/rss-checker/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="bot_${TIMESTAMP}.py"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Backup the current bot.py
cp bot.py "$BACKUP_DIR/$BACKUP_NAME"

echo "✓ Backup created: $BACKUP_DIR/$BACKUP_NAME"
echo "  To rollback: cp $BACKUP_DIR/$BACKUP_NAME bot.py"

# Keep only the last 10 backups
ls -t "$BACKUP_DIR"/bot_*.py | tail -n +11 | xargs -r rm
echo "✓ Old backups cleaned (keeping last 10)"
