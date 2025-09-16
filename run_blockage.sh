#!/bin/bash
#
# Blockage - Comprehensive Pi-Hole Blocklist Aggregator
# Convenient launcher script with pre-configured options
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default values
OUTPUT_DIR="$SCRIPT_DIR/output"
VERBOSE=false
CATEGORIES=""
FORMATS="pihole domains"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    cat << EOF
Blockage - Comprehensive Pi-Hole Blocklist Aggregator

Usage: $0 [OPTIONS]

OPTIONS:
    -h, --help              Show this help message
    -v, --verbose           Enable verbose logging
    -o, --output DIR        Output directory (default: ./output)
    -c, --categories LIST   Comma-separated list of categories
    -f, --formats LIST      Output formats: pihole,domains (default: both)
    
    --max-protection        Enable maximum protection (all categories)
    --basic-protection      Enable basic protection (ads, tracking, malware)
    --privacy-focused       Enable privacy-focused protection
    --family-safe          Enable family-safe protection

EXAMPLES:
    # Maximum protection (default)
    $0

    # Basic protection only
    $0 --basic-protection

    # Privacy-focused protection
    $0 --privacy-focused

    # Custom categories
    $0 -c "advertising,tracking,malware"

    # Custom output directory with verbose logging
    $0 -o /var/lib/pihole/custom-lists -v

CATEGORIES:
    advertising, tracking, malware, phishing, privacy, social_media,
    adult_content, cryptocurrency, fake_news, gambling, regional_threats,
    comprehensive

EOF
}

# Function to check dependencies
check_dependencies() {
    print_status "Checking dependencies..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed."
        exit 1
    fi
    
    # Check pip packages
    if ! python3 -c "import requests" &> /dev/null; then
        print_status "Installing required Python packages..."
        python3 -m pip install -r "$SCRIPT_DIR/requirements.txt"
    fi
    
    print_success "Dependencies check passed"
}

# Function to create output directory
prepare_output() {
    print_status "Preparing output directory: $OUTPUT_DIR"
    mkdir -p "$OUTPUT_DIR"
    
    # Create backup of existing files
    if [ "$(ls -A "$OUTPUT_DIR" 2>/dev/null)" ]; then
        backup_dir="$OUTPUT_DIR/backup_$(date +%Y%m%d_%H%M%S)"
        print_status "Creating backup: $backup_dir"
        mkdir -p "$backup_dir"
        cp "$OUTPUT_DIR"/*.txt "$backup_dir"/ 2>/dev/null || true
        cp "$OUTPUT_DIR"/*.json "$backup_dir"/ 2>/dev/null || true
    fi
}

# Function to run the aggregator
run_aggregator() {
    print_status "Starting Blockage aggregation..."
    
    # Build command
    cmd="python3 $SCRIPT_DIR/blocklist_aggregator.py --output-dir $OUTPUT_DIR"
    
    if [ "$VERBOSE" = true ]; then
        cmd="$cmd --verbose"
    fi
    
    if [ -n "$CATEGORIES" ]; then
        cmd="$cmd --categories $CATEGORIES"
    fi
    
    if [ -n "$FORMATS" ]; then
        cmd="$cmd --formats $FORMATS"
    fi
    
    print_status "Executing: $cmd"
    
    # Run the aggregator
    if eval "$cmd"; then
        print_success "Aggregation completed successfully!"
        show_results
    else
        print_error "Aggregation failed!"
        exit 1
    fi
}

# Function to show results
show_results() {
    print_status "Generated files in $OUTPUT_DIR:"
    
    if [ -f "$OUTPUT_DIR/report.txt" ]; then
        echo
        cat "$OUTPUT_DIR/report.txt"
        echo
    fi
    
    print_status "Available files:"
    ls -lh "$OUTPUT_DIR"/ | grep -E '\.(txt|json)$' || true
    
    echo
    print_success "Ready for Pi-Hole integration!"
    print_status "Add these URLs to your Pi-Hole blocklist:"
    echo "  - file://$OUTPUT_DIR/blocklist_comprehensive.txt"
    echo "  - Or upload individual category files as needed"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -c|--categories)
            CATEGORIES="$2"
            shift 2
            ;;
        -f|--formats)
            FORMATS="$2"
            shift 2
            ;;
        --max-protection)
            CATEGORIES=""  # Use all categories
            shift
            ;;
        --basic-protection)
            CATEGORIES="advertising tracking malware phishing"
            shift
            ;;
        --privacy-focused)
            CATEGORIES="advertising tracking privacy social_media"
            shift
            ;;
        --family-safe)
            CATEGORIES="advertising tracking malware phishing adult_content gambling fake_news"
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
main() {
    echo
    echo "🛡️  Blockage - Comprehensive Pi-Hole Blocklist Aggregator"
    echo "   Go Big or Go Home - Maximum Protection Mode"
    echo
    
    check_dependencies
    prepare_output
    run_aggregator
    
    echo
    print_success "🎉 Blockage aggregation complete!"
    print_status "Your Pi-Hole is now ready for maximum protection!"
}

# Run main function
main