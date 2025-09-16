# Blockage Quick Start Guide

🚀 **Get maximum Pi-Hole protection in 5 minutes!**

## Super Quick Start (Recommended)

1. **Clone and run immediately**:
   ```bash
   git clone https://github.com/greyfory/Blockage.git
   cd Blockage
   ./run_blockage.sh --max-protection
   ```

2. **Add to Pi-Hole**:
   - Copy the file path: `./output/blocklist_comprehensive.txt`
   - In Pi-Hole admin → Adlists → Add: `file:///full/path/to/blocklist_comprehensive.txt`
   - Update gravity

**That's it! You now have maximum protection with 200,000+ blocked domains.**

## Protection Levels

### 🛡️ Maximum Protection (Default)
```bash
./run_blockage.sh --max-protection
```
- **All categories included**
- **200,000+ domains blocked**
- **Ultimate security and privacy**

### 🔒 Basic Protection
```bash
./run_blockage.sh --basic-protection
```
- Advertising, tracking, malware, phishing
- ~150,000 domains blocked
- Good for general use

### 🕵️ Privacy Focused
```bash
./run_blockage.sh --privacy-focused
```
- Advertising, tracking, privacy, social media
- ~180,000 domains blocked
- Maximum privacy protection

### 👨‍👩‍👧‍👦 Family Safe
```bash
./run_blockage.sh --family-safe
```
- Basic protection + adult content + gambling + fake news
- ~170,000 domains blocked
- Safe for family networks

## Automatic Updates

Set up automatic updates (runs daily at 3 AM):
```bash
# Create configuration
./auto_update.sh --config-only

# Edit the config file to add your Pi-Hole server
nano auto_update_config.conf

# Add to crontab
echo "0 3 * * * $(pwd)/auto_update.sh" | crontab -
```

## Pi-Hole Integration Methods

### Method 1: Local File (Fastest)
```bash
# After running Blockage
sudo cp output/blocklist_comprehensive.txt /var/lib/pihole/
# In Pi-Hole: Add file:///var/lib/pihole/blocklist_comprehensive.txt
```

### Method 2: Web Server
```bash
# Copy to web server directory
sudo cp output/* /var/www/html/blocklists/
# In Pi-Hole: Add http://yourserver/blocklists/blocklist_comprehensive.txt
```

### Method 3: GitHub Pages (Public)
1. Fork this repository
2. Enable GitHub Pages
3. Run Blockage and commit the output files
4. Use: `https://yourusername.github.io/Blockage/output/blocklist_comprehensive.txt`

## Output Files Explained

| File | Description | Use Case |
|------|-------------|----------|
| `blocklist_comprehensive.txt` | All categories combined (Pi-Hole format) | **Main file for Pi-Hole** |
| `blocklist_advertising.txt` | Advertising only | Selective blocking |
| `blocklist_malware.txt` | Malware protection only | Security-only mode |
| `domains_comprehensive.txt` | Plain domain list | Other DNS servers |
| `statistics.json` | Detailed statistics | Monitoring |
| `report.txt` | Human-readable summary | Quick overview |

## Common Use Cases

### 🏠 Home Network
```bash
./run_blockage.sh --family-safe
```
Add `blocklist_comprehensive.txt` to Pi-Hole.

### 🏢 Business Network
```bash
./run_blockage.sh --categories advertising tracking malware phishing privacy
```
Add category-specific files for granular control.

### 🔬 Security Research
```bash
./run_blockage.sh --max-protection --verbose
```
Use all files and monitor `statistics.json`.

### 🌐 Public WiFi
```bash
./run_blockage.sh --categories malware phishing adult_content
```
Focus on security and content filtering.

## Customization

### Add Custom Domains
Edit `whitelist.txt` to add domains that should never be blocked:
```
essential-service.com
important-website.org
```

### Custom Categories
```bash
./run_blockage.sh --categories "advertising,tracking,malware,custom_category"
```

### Custom Configuration
1. Copy `blocklist_sources.json` to `my_config.json`
2. Add your own sources
3. Run: `python3 blocklist_aggregator.py --config my_config.json`

## Troubleshooting

### ❌ "No domains generated"
- Check internet connection
- Try basic protection first: `./run_blockage.sh --basic-protection`

### ❌ "Pi-Hole not updating"
- Ensure file path is correct
- Try copying file directly to Pi-Hole server
- Check Pi-Hole logs: `pihole -t`

### ❌ "Some websites broken"
- Add domains to `whitelist.txt`
- Use less aggressive protection level
- Check Pi-Hole query log for blocked domains

### ❌ "Downloads failing"
- Some sources may be temporarily unavailable
- The system will continue with available sources
- Check logs for specific errors

## Performance Tips

### For Large Networks
```bash
# Use compressed output
./run_blockage.sh --categories advertising tracking malware
```

### For Slow Connections
```bash
# Start with basic protection
./run_blockage.sh --basic-protection
# Gradually add more categories
```

### For Maximum Speed
```bash
# Use category-specific files instead of comprehensive
# Add multiple smaller lists to Pi-Hole instead of one large list
```

## Security Notes

- 🔒 All sources are from trusted security researchers
- 🔄 Lists are updated automatically with retry logic
- ✅ Domains are validated before inclusion
- 🚫 Essential services are whitelisted by default
- 📊 Full transparency with statistics and logs

## Getting Help

1. **Check the logs**: `cat blocklist_aggregator.log`
2. **Review statistics**: `cat output/statistics.json`
3. **Test with verbose mode**: `./run_blockage.sh --verbose`
4. **Start with basic protection**: `./run_blockage.sh --basic-protection`

## Next Steps

1. ✅ **Set up automatic updates**
2. ✅ **Monitor Pi-Hole query logs**
3. ✅ **Adjust whitelist as needed**
4. ✅ **Share your results with the community**

---

🎯 **Go Big or Go Home** - You now have enterprise-level protection for your Pi-Hole!