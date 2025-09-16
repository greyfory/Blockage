#!/bin/bash
#
# Blockage Auto-Updater
# Automatically updates blocklists and optionally deploys to Pi-Hole
#

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/auto_update_config.conf"
LOG_FILE="$SCRIPT_DIR/auto_update.log"
OUTPUT_DIR="$SCRIPT_DIR/output"
BACKUP_RETENTION_DAYS=7

# Default configuration
PIHOLE_SERVER=""
PIHOLE_API_TOKEN=""
UPDATE_FREQUENCY="daily"
CATEGORIES="advertising tracking malware phishing"
ENABLE_NOTIFICATIONS=false
WEBHOOK_URL=""

# Load configuration if it exists
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
fi

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Error handling
handle_error() {
    log "ERROR: $1"
    if [ "$ENABLE_NOTIFICATIONS" = true ] && [ -n "$WEBHOOK_URL" ]; then
        send_notification "❌ Blockage Update Failed" "$1"
    fi
    exit 1
}

# Notification function
send_notification() {
    local title="$1"
    local message="$2"
    
    if [ -n "$WEBHOOK_URL" ]; then
        curl -s -X POST "$WEBHOOK_URL" \
            -H "Content-Type: application/json" \
            -d "{\"title\": \"$title\", \"message\": \"$message\"}" \
            || log "WARNING: Failed to send notification"
    fi
}

# Check if update is needed
check_update_needed() {
    local last_update_file="$OUTPUT_DIR/.last_update"
    
    if [ ! -f "$last_update_file" ]; then
        return 0  # First run
    fi
    
    local last_update=$(cat "$last_update_file")
    local current_time=$(date +%s)
    local time_diff=$((current_time - last_update))
    
    case "$UPDATE_FREQUENCY" in
        "hourly")
            [ $time_diff -gt 3600 ]
            ;;
        "daily")
            [ $time_diff -gt 86400 ]
            ;;
        "weekly")
            [ $time_diff -gt 604800 ]
            ;;
        *)
            return 0  # Default to always update
            ;;
    esac
}

# Update blocklists
update_blocklists() {
    log "Starting blocklist update..."
    
    # Create backup
    if [ -d "$OUTPUT_DIR" ] && [ "$(ls -A "$OUTPUT_DIR" 2>/dev/null)" ]; then
        local backup_dir="$OUTPUT_DIR/backup_$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$backup_dir"
        cp "$OUTPUT_DIR"/*.txt "$backup_dir"/ 2>/dev/null || true
        cp "$OUTPUT_DIR"/*.json "$backup_dir"/ 2>/dev/null || true
        log "Created backup: $backup_dir"
    fi
    
    # Run aggregator
    local cmd="python3 $SCRIPT_DIR/blocklist_aggregator.py --output-dir $OUTPUT_DIR"
    
    if [ -n "$CATEGORIES" ]; then
        cmd="$cmd --categories $CATEGORIES"
    fi
    
    if ! eval "$cmd" 2>&1 | tee -a "$LOG_FILE"; then
        handle_error "Failed to update blocklists"
    fi
    
    # Update timestamp
    date +%s > "$OUTPUT_DIR/.last_update"
    
    log "Blocklist update completed successfully"
}

# Deploy to Pi-Hole
deploy_to_pihole() {
    if [ -z "$PIHOLE_SERVER" ]; then
        log "No Pi-Hole server configured, skipping deployment"
        return
    fi
    
    log "Deploying to Pi-Hole server: $PIHOLE_SERVER"
    
    # Copy files to Pi-Hole server
    local blocklist_file="$OUTPUT_DIR/blocklist_comprehensive.txt"
    local remote_path="/var/lib/pihole/custom-blocklist.txt"
    
    if [ ! -f "$blocklist_file" ]; then
        handle_error "Blocklist file not found: $blocklist_file"
    fi
    
    # SCP the file
    if ! scp "$blocklist_file" "$PIHOLE_SERVER:$remote_path"; then
        handle_error "Failed to copy blocklist to Pi-Hole server"
    fi
    
    # Restart Pi-Hole DNS (optional, requires API token)
    if [ -n "$PIHOLE_API_TOKEN" ]; then
        if ! ssh "$PIHOLE_SERVER" "pihole restartdns"; then
            log "WARNING: Failed to restart Pi-Hole DNS"
        fi
    fi
    
    log "Successfully deployed to Pi-Hole"
}

# Cleanup old backups
cleanup_backups() {
    log "Cleaning up old backups..."
    
    find "$OUTPUT_DIR" -name "backup_*" -type d -mtime +$BACKUP_RETENTION_DAYS -exec rm -rf {} \; 2>/dev/null || true
    
    log "Backup cleanup completed"
}

# Generate update report
generate_report() {
    local report_file="$OUTPUT_DIR/update_report.txt"
    local stats_file="$OUTPUT_DIR/statistics.json"
    
    if [ -f "$stats_file" ]; then
        local total_domains=$(grep -o '"total_domains": [0-9]*' "$stats_file" | cut -d' ' -f2)
        local timestamp=$(grep -o '"generation_time": "[^"]*"' "$stats_file" | cut -d'"' -f4)
        
        cat > "$report_file" << EOF
Blockage Auto-Update Report
===========================

Update Time: $timestamp
Total Domains: $total_domains
Categories: $CATEGORIES
Output Directory: $OUTPUT_DIR

Pi-Hole Integration:
- Server: ${PIHOLE_SERVER:-"Not configured"}
- Deployment: ${PIHOLE_SERVER:+"Enabled"}

Next Update: Based on frequency setting ($UPDATE_FREQUENCY)

For detailed statistics, see: $stats_file
EOF
        
        log "Generated update report: $report_file"
        
        # Send notification if enabled
        if [ "$ENABLE_NOTIFICATIONS" = true ]; then
            send_notification "✅ Blockage Updated" "Successfully updated with $total_domains domains"
        fi
    fi
}

# Main execution
main() {
    log "Starting Blockage auto-updater"
    
    # Check if update is needed
    if ! check_update_needed; then
        log "Update not needed yet based on frequency setting"
        exit 0
    fi
    
    # Update blocklists
    update_blocklists
    
    # Deploy to Pi-Hole if configured
    deploy_to_pihole
    
    # Generate report
    generate_report
    
    # Cleanup old backups
    cleanup_backups
    
    log "Auto-update completed successfully"
}

# Show usage
show_usage() {
    cat << EOF
Blockage Auto-Updater

Usage: $0 [OPTIONS]

OPTIONS:
    -h, --help          Show this help message
    --force             Force update regardless of frequency
    --config-only       Only create configuration file
    --test              Test mode (no actual deployment)

CONFIGURATION:
    Edit $CONFIG_FILE to customize settings:
    
    PIHOLE_SERVER="user@pihole.local"
    PIHOLE_API_TOKEN="your-api-token"
    UPDATE_FREQUENCY="daily"
    CATEGORIES="advertising tracking malware phishing"
    ENABLE_NOTIFICATIONS=true
    WEBHOOK_URL="https://your-webhook-url"

AUTOMATION:
    Add to crontab for automatic updates:
    # Daily updates at 3 AM
    0 3 * * * $0 >> $LOG_FILE 2>&1

EOF
}

# Create configuration file
create_config() {
    cat > "$CONFIG_FILE" << 'EOF'
# Blockage Auto-Updater Configuration

# Pi-Hole server connection (SSH format: user@hostname)
PIHOLE_SERVER=""

# Pi-Hole API token (optional, for DNS restart)
PIHOLE_API_TOKEN=""

# Update frequency: hourly, daily, weekly
UPDATE_FREQUENCY="daily"

# Categories to include (space-separated)
CATEGORIES="advertising tracking malware phishing privacy"

# Notifications
ENABLE_NOTIFICATIONS=false
WEBHOOK_URL=""

# Backup retention (days)
BACKUP_RETENTION_DAYS=7
EOF
    
    echo "Created configuration file: $CONFIG_FILE"
    echo "Please edit this file to customize your settings."
}

# Parse arguments
case "${1:-}" in
    -h|--help)
        show_usage
        exit 0
        ;;
    --force)
        rm -f "$OUTPUT_DIR/.last_update" 2>/dev/null || true
        main
        ;;
    --config-only)
        create_config
        exit 0
        ;;
    --test)
        PIHOLE_SERVER=""  # Disable deployment
        main
        ;;
    "")
        main
        ;;
    *)
        echo "Unknown option: $1"
        show_usage
        exit 1
        ;;
esac