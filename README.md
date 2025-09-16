# Blockage - Comprehensive Pi-Hole Blocklist Collection

🛡️ **Go Big or Go Home** - The most comprehensive Pi-Hole blocklist aggregator that searches the entire web for all kinds of blocklists, including everything risky and threatening.

## 🚀 Features

- **Comprehensive Coverage**: Aggregates blocklists from 40+ sources across multiple categories
- **Multiple Categories**: Advertising, tracking, malware, phishing, privacy, social media, adult content, cryptocurrency mining, fake news, gambling, and regional threats
- **Smart Processing**: Supports multiple input formats (hosts, domains, AdBlock, archives)
- **Deduplication**: Removes duplicate entries and validates domains
- **Whitelist Support**: Prevents blocking of essential services
- **Multiple Output Formats**: Pi-Hole compatible hosts files and plain domain lists
- **Statistics & Reporting**: Detailed statistics and human-readable reports
- **Error Handling**: Robust retry logic and error handling
- **Categorized Output**: Separate files for each category plus comprehensive collection

## 📁 Repository Structure

```
Blockage/
├── blocklist_aggregator.py    # Main aggregation script
├── blocklist_sources.json     # Comprehensive source configuration
├── whitelist.txt              # Essential domains to never block
├── requirements.txt           # Python dependencies
├── README.md                  # This documentation
└── output/                    # Generated blocklist files (created on run)
    ├── blocklist_comprehensive.txt    # All categories combined (Pi-Hole format)
    ├── blocklist_advertising.txt      # Advertising blocklist
    ├── blocklist_malware.txt          # Malware protection
    ├── domains_comprehensive.txt      # All domains (plain format)
    ├── statistics.json               # Detailed statistics
    └── report.txt                    # Human-readable report
```

## 🎯 Blocklist Categories

### Core Protection
- **Advertising**: Steven Black's Unified Hosts, AdGuard, EasyList, AdAway, Dan Pollock's
- **Tracking**: EasyPrivacy, Disconnect.me, AdGuard Tracking Protection, Peter Lowe's
- **Malware**: Malware Domain List, URLVoid, Spam404, OISD Big List
- **Phishing**: PhishTank, OpenPhish, Anti-Phishing Working Group

### Advanced Protection
- **Privacy**: Fanboy's Enhanced Tracking, I Don't Care About Cookies, Disconnect Malvertising
- **Social Media**: Fanboy's Social Blocking, AdGuard Social Media Filter
- **Adult Content**: Shalla's Blacklists, UT1 Blacklist, Steven Black's Porn Hosts
- **Cryptocurrency**: Coin Blocker Lists, NoCoin Filter List

### Specialized Protection
- **Fake News**: Steven Black's Fake News, Fake News Blocklist
- **Gambling**: Steven Black's Gambling, Shalla's Gambling
- **Regional Threats**: Russia, China, France, Germany specific lists

### Ultimate Protection
- **Comprehensive**: 1Hosts Pro, NextDNS Recommended, HaGeZi's Ultimate Blocklist

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/greyfory/Blockage.git
   cd Blockage
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Make the script executable**:
   ```bash
   chmod +x blocklist_aggregator.py
   ```

## 🚀 Usage

### Basic Usage
Generate all blocklists with maximum protection:
```bash
python blocklist_aggregator.py
```

### Advanced Usage

**Process specific categories only**:
```bash
python blocklist_aggregator.py --categories advertising malware tracking
```

**Custom output directory**:
```bash
python blocklist_aggregator.py --output-dir /path/to/custom/output
```

**Generate specific formats**:
```bash
python blocklist_aggregator.py --formats pihole
python blocklist_aggregator.py --formats domains
```

**Verbose logging**:
```bash
python blocklist_aggregator.py --verbose
```

**Complete example with all options**:
```bash
python blocklist_aggregator.py \
  --categories advertising tracking malware phishing \
  --output-dir ./custom_output \
  --formats pihole domains \
  --verbose
```

## 📋 Command Line Options

- `--categories`: Specify which categories to process (default: all)
- `--output-dir`: Output directory for generated files (default: `output`)
- `--config`: Configuration file path (default: `blocklist_sources.json`)
- `--formats`: Output formats - `pihole`, `domains` (default: both)
- `--verbose`: Enable verbose logging
- `--help`: Show help message

## 🔧 Pi-Hole Integration

### Method 1: Direct Import (Recommended)
1. Run the aggregator to generate blocklists
2. Copy the generated files to your Pi-Hole server
3. Add the blocklist URLs to Pi-Hole admin interface:
   ```
   file:///path/to/blocklist_comprehensive.txt
   ```

### Method 2: Web Server Hosting
1. Host the generated files on a web server
2. Add the URLs to Pi-Hole:
   ```
   https://yourserver.com/blocklist_comprehensive.txt
   ```

### Method 3: Category-Specific Lists
For more granular control, use individual category files:
```
https://yourserver.com/blocklist_advertising.txt
https://yourserver.com/blocklist_malware.txt
https://yourserver.com/blocklist_tracking.txt
```

## 📊 Output Files

### Pi-Hole Format (`blocklist_*.txt`)
Standard Pi-Hole hosts file format:
```
0.0.0.0 malicious-domain.com
0.0.0.0 ad-server.net
0.0.0.0 tracking-pixel.org
```

### Domain Lists (`domains_*.txt`)
Plain domain list format:
```
malicious-domain.com
ad-server.net
tracking-pixel.org
```

### Statistics (`statistics.json`)
Detailed JSON statistics including:
- Total domain counts
- Per-category breakdowns
- Download success/failure rates
- Top blocked domains

### Report (`report.txt`)
Human-readable summary report with key metrics and statistics.

## ⚙️ Configuration

### Whitelist Customization
Edit `whitelist.txt` to add domains that should never be blocked:
```
essential-service.com
important-website.org
```

### Source Configuration
The `blocklist_sources.json` file contains all source configurations. You can:
- Add new sources
- Modify existing sources
- Disable sources by removing them
- Add custom categories

## 🔍 Monitoring & Logs

The script generates detailed logs in `blocklist_aggregator.log` including:
- Download progress and status
- Processing statistics
- Error messages and retry attempts
- Domain extraction counts
- Final aggregation results

## 🛡️ Security Features

- **Input Validation**: All domains are validated using regex patterns
- **Whitelist Protection**: Essential services are protected from blocking
- **Error Handling**: Robust error handling prevents crashes
- **Rate Limiting**: Built-in delays prevent overwhelming servers
- **Retry Logic**: Automatic retries for failed downloads

## 📈 Performance

- **Parallel Processing**: Efficient processing of multiple sources
- **Memory Efficient**: Uses sets for deduplication
- **Bandwidth Conscious**: Implements rate limiting and caching
- **Scalable**: Can handle millions of domains

## 🤝 Contributing

1. Fork the repository
2. Add new blocklist sources to `blocklist_sources.json`
3. Test your changes
4. Submit a pull request

### Adding New Sources
To add a new blocklist source:
```json
{
  "name": "New Blocklist",
  "url": "https://example.com/blocklist.txt",
  "description": "Description of the blocklist",
  "format": "hosts|domain|adblock|url|archive",
  "update_frequency": "daily|weekly|monthly"
}
```

## 🐛 Troubleshooting

### Common Issues

**Download Failures**:
- Check internet connectivity
- Verify source URLs are accessible
- Review logs for specific error messages

**Empty Output Files**:
- Ensure sources are accessible
- Check whitelist isn't too restrictive
- Verify domain validation patterns

**Performance Issues**:
- Reduce categories being processed
- Increase delays between downloads
- Use faster internet connection

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

This project aggregates blocklists from numerous sources maintained by security researchers, volunteers, and organizations worldwide. Special thanks to:

- Steven Black's Unified Hosts
- AdGuard Team
- EasyList Community
- Disconnect.me
- All other source maintainers

## ⚠️ Disclaimer

This tool is provided for educational and security purposes. Users are responsible for:
- Complying with source terms of service
- Respecting rate limits
- Testing before production deployment
- Understanding the impact of blocking decisions

**Go Big or Go Home** - Maximum protection comes with maximum responsibility!