#!/bin/bash
# Schedule Morning Alerts Dashboard
#
# This script helps you set up automatic daily morning alerts.
# It runs the full pipeline and generates the dashboard every morning.

# Configuration
HOUR="08"        # 8 AM
MINUTE="00"      # At exactly 00 minutes
DAYS="1"         # Show last 1 day of alerts
AUTO_OPEN="true" # Automatically open in browser

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Function to install cron job
install_cron() {
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║     Installing Morning Alerts Dashboard Cron Job         ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo

    # Create the cron command
    if [ "$AUTO_OPEN" = "true" ]; then
        CRON_CMD="cd $SCRIPT_DIR && python morning_dashboard.py --days $DAYS --auto-open >> data/logs/morning_dashboard.log 2>&1"
    else
        CRON_CMD="cd $SCRIPT_DIR && python morning_dashboard.py --days $DAYS >> data/logs/morning_dashboard.log 2>&1"
    fi

    # Create log directory
    mkdir -p "$SCRIPT_DIR/data/logs"

    # Add to crontab
    CRON_ENTRY="$MINUTE $HOUR * * * $CRON_CMD"

    # Check if entry already exists
    if crontab -l 2>/dev/null | grep -q "morning_dashboard.py"; then
        echo "⚠️  Morning dashboard cron job already exists!"
        echo
        echo "Current cron jobs:"
        crontab -l | grep morning_dashboard
        echo
        read -p "Replace it? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "❌ Cancelled"
            exit 1
        fi

        # Remove old entry
        crontab -l | grep -v "morning_dashboard.py" | crontab -
    fi

    # Add new entry
    (crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -

    echo "✅ Cron job installed successfully!"
    echo
    echo "📅 Schedule: Every day at $HOUR:$MINUTE"
    echo "📊 Shows alerts from last $DAYS day(s)"
    echo "🌐 Auto-open: $AUTO_OPEN"
    echo
    echo "To view all cron jobs: crontab -l"
    echo "To remove: crontab -e (then delete the line)"
    echo
    echo "Logs will be written to: data/logs/morning_dashboard.log"
    echo
}

# Function to run manual test
run_test() {
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║          Testing Morning Alerts Dashboard                ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo

    cd "$SCRIPT_DIR"

    echo "🧪 Running test generation..."
    python morning_dashboard.py --days $DAYS --auto-open

    echo
    echo "✅ Test complete!"
    echo
}

# Function to show current schedule
show_schedule() {
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║        Current Morning Dashboard Schedule                ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo

    if crontab -l 2>/dev/null | grep -q "morning_dashboard.py"; then
        echo "📅 Active cron jobs:"
        echo
        crontab -l | grep morning_dashboard
        echo
    else
        echo "⚠️  No morning dashboard cron job found"
        echo
        echo "Run './schedule_morning_alerts.sh install' to set it up"
    fi
}

# Function to uninstall cron job
uninstall_cron() {
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║       Uninstalling Morning Dashboard Cron Job            ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo

    if crontab -l 2>/dev/null | grep -q "morning_dashboard.py"; then
        crontab -l | grep -v "morning_dashboard.py" | crontab -
        echo "✅ Cron job removed successfully!"
    else
        echo "⚠️  No morning dashboard cron job found"
    fi
    echo
}

# Main menu
case "${1:-}" in
    install)
        install_cron
        ;;
    test)
        run_test
        ;;
    status)
        show_schedule
        ;;
    uninstall)
        uninstall_cron
        ;;
    *)
        echo "╔══════════════════════════════════════════════════════════╗"
        echo "║        Morning Alerts Dashboard Scheduler                ║"
        echo "╚══════════════════════════════════════════════════════════╝"
        echo
        echo "Usage: $0 {install|test|status|uninstall}"
        echo
        echo "Commands:"
        echo "  install    - Install cron job to run dashboard every morning"
        echo "  test       - Run a test generation now"
        echo "  status     - Show current schedule"
        echo "  uninstall  - Remove the cron job"
        echo
        echo "Configuration (edit this script to change):"
        echo "  Time: $HOUR:$MINUTE (24-hour format)"
        echo "  Days: $DAYS"
        echo "  Auto-open: $AUTO_OPEN"
        echo
        echo "Examples:"
        echo "  $0 install    # Set up daily morning alerts"
        echo "  $0 test       # Test it now"
        echo "  $0 status     # Check if it's scheduled"
        echo
        exit 1
        ;;
esac
