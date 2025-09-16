#!/usr/bin/env python3
"""
Comprehensive Pi-Hole Blocklist Aggregator
==========================================

This script aggregates blocklists from multiple sources across the web,
processes them, deduplicates entries, and creates organized output files
suitable for Pi-Hole consumption.

Features:
- Supports multiple input formats (hosts, domains, adblock, etc.)
- Deduplication and validation
- Categorized output
- Whitelist support
- Statistics and reporting
- Error handling and retry logic

Author: Blockage Project
License: MIT
"""

import json
import requests
import re
import sys
import os
import time
import gzip
import tarfile
import tempfile
from urllib.parse import urlparse
from collections import defaultdict, Counter
from datetime import datetime
import argparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('blocklist_aggregator.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class BlocklistAggregator:
    """Main class for aggregating and processing blocklists."""
    
    def __init__(self, config_file='blocklist_sources.json', output_dir='output'):
        """Initialize the aggregator with configuration."""
        self.config_file = config_file
        self.output_dir = output_dir
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; Blockage-Aggregator/1.0; +https://github.com/greyfory/Blockage)'
        })
        
        # Domain storage
        self.domains = defaultdict(set)  # category -> set of domains
        self.all_domains = set()
        self.whitelist = set()
        self.statistics = defaultdict(int)
        
        # Validation patterns
        self.domain_pattern = re.compile(r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$')
        self.ip_pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
        
        # Load configuration
        self.load_config()
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
    
    def load_config(self):
        """Load blocklist sources configuration."""
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
            logger.info(f"Loaded configuration with {len(self.config['blocklist_sources'])} categories")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            sys.exit(1)
    
    def load_whitelist(self, whitelist_file='whitelist.txt'):
        """Load whitelist domains to exclude from blocking."""
        if os.path.exists(whitelist_file):
            try:
                with open(whitelist_file, 'r') as f:
                    for line in f:
                        domain = line.strip().lower()
                        if domain and not domain.startswith('#'):
                            self.whitelist.add(domain)
                logger.info(f"Loaded {len(self.whitelist)} whitelisted domains")
            except Exception as e:
                logger.error(f"Failed to load whitelist: {e}")
    
    def is_valid_domain(self, domain):
        """Validate if a string is a valid domain name."""
        if not domain or len(domain) > 253:
            return False
        
        # Remove leading/trailing dots
        domain = domain.strip('.')
        
        # Check if it's an IP address (not a domain)
        if self.ip_pattern.match(domain):
            return False
        
        # Check domain pattern
        return bool(self.domain_pattern.match(domain))
    
    def extract_domains_from_hosts(self, content):
        """Extract domains from hosts file format."""
        domains = set()
        for line in content.split('\n'):
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Handle hosts file format (IP domain)
            parts = line.split()
            if len(parts) >= 2:
                # Skip localhost entries
                if parts[1] in ['localhost', 'localhost.localdomain', 'local', 'broadcasthost']:
                    continue
                
                domain = parts[1].lower()
                if self.is_valid_domain(domain):
                    domains.add(domain)
        
        return domains
    
    def extract_domains_from_adblock(self, content):
        """Extract domains from AdBlock format."""
        domains = set()
        for line in content.split('\n'):
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('!') or line.startswith('['):
                continue
            
            # Handle different AdBlock formats
            if line.startswith('||') and line.endswith('^'):
                # Format: ||example.com^
                domain = line[2:-1].lower()
                if self.is_valid_domain(domain):
                    domains.add(domain)
            elif line.startswith('||'):
                # Format: ||example.com
                domain = line[2:].lower()
                if self.is_valid_domain(domain):
                    domains.add(domain)
            elif '##' not in line and '$' not in line:
                # Simple domain format
                domain = line.lower()
                if self.is_valid_domain(domain):
                    domains.add(domain)
        
        return domains
    
    def extract_domains_from_plain(self, content):
        """Extract domains from plain domain list."""
        domains = set()
        for line in content.split('\n'):
            line = line.strip().lower()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            if self.is_valid_domain(line):
                domains.add(line)
        
        return domains
    
    def extract_domains_from_url_list(self, content):
        """Extract domains from URL list."""
        domains = set()
        for line in content.split('\n'):
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            try:
                parsed = urlparse(line)
                domain = parsed.netloc.lower()
                if self.is_valid_domain(domain):
                    domains.add(domain)
            except:
                continue
        
        return domains
    
    def download_blocklist(self, url, retries=3):
        """Download a blocklist with retry logic."""
        for attempt in range(retries):
            try:
                logger.info(f"Downloading {url} (attempt {attempt + 1})")
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                # Handle compressed content
                if response.headers.get('content-encoding') == 'gzip':
                    content = gzip.decompress(response.content).decode('utf-8')
                else:
                    content = response.text
                
                self.statistics['downloads_successful'] += 1
                return content
                
            except Exception as e:
                logger.warning(f"Download attempt {attempt + 1} failed for {url}: {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    self.statistics['downloads_failed'] += 1
                    logger.error(f"Failed to download {url} after {retries} attempts")
                    return None
    
    def process_archive(self, url, category_name):
        """Process archived blocklists (tar.gz format)."""
        logger.info(f"Processing archive from {url}")
        
        try:
            response = self.session.get(url, timeout=60)
            response.raise_for_status()
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.tar.gz') as tmp_file:
                tmp_file.write(response.content)
                tmp_path = tmp_file.name
            
            domains = set()
            
            # Extract and process archive
            with tarfile.open(tmp_path, 'r:gz') as tar:
                for member in tar.getmembers():
                    if member.isfile() and category_name in member.name.lower():
                        f = tar.extractfile(member)
                        if f:
                            content = f.read().decode('utf-8', errors='ignore')
                            domains.update(self.extract_domains_from_plain(content))
            
            # Clean up
            os.unlink(tmp_path)
            
            return domains
            
        except Exception as e:
            logger.error(f"Failed to process archive {url}: {e}")
            return set()
    
    def process_blocklist(self, source, category):
        """Process a single blocklist source."""
        url = source['url']
        format_type = source.get('format', 'domain')
        
        logger.info(f"Processing {source['name']} ({format_type})")
        
        domains = set()
        
        try:
            if format_type == 'archive':
                domains = self.process_archive(url, category)
            else:
                content = self.download_blocklist(url)
                if not content:
                    return domains
                
                if format_type == 'hosts':
                    domains = self.extract_domains_from_hosts(content)
                elif format_type == 'adblock':
                    domains = self.extract_domains_from_adblock(content)
                elif format_type == 'domain':
                    domains = self.extract_domains_from_plain(content)
                elif format_type == 'url':
                    domains = self.extract_domains_from_url_list(content)
                else:
                    logger.warning(f"Unknown format: {format_type}")
                    domains = self.extract_domains_from_plain(content)
            
            # Filter out whitelisted domains
            domains = {d for d in domains if d not in self.whitelist}
            
            logger.info(f"Extracted {len(domains)} domains from {source['name']}")
            self.statistics[f'domains_from_{category}'] += len(domains)
            
            return domains
            
        except Exception as e:
            logger.error(f"Error processing {source['name']}: {e}")
            return set()
    
    def aggregate_all_lists(self, categories=None):
        """Aggregate all blocklists from specified categories."""
        if categories is None:
            categories = list(self.config['blocklist_sources'].keys())
        
        logger.info(f"Starting aggregation for categories: {', '.join(categories)}")
        
        for category in categories:
            if category not in self.config['blocklist_sources']:
                logger.warning(f"Category '{category}' not found in configuration")
                continue
            
            logger.info(f"Processing category: {category}")
            sources = self.config['blocklist_sources'][category]
            
            for source in sources:
                domains = self.process_blocklist(source, category)
                self.domains[category].update(domains)
                self.all_domains.update(domains)
                
                # Rate limiting
                time.sleep(1)
        
        logger.info(f"Aggregation complete. Total unique domains: {len(self.all_domains)}")
    
    def generate_pihole_format(self, domains, filename):
        """Generate Pi-Hole compatible hosts file."""
        output_path = os.path.join(self.output_dir, filename)
        
        with open(output_path, 'w') as f:
            f.write(f"# Pi-Hole Blocklist - {filename}\n")
            f.write(f"# Generated: {datetime.now().isoformat()}\n")
            f.write(f"# Total domains: {len(domains)}\n")
            f.write(f"# Source: Blockage Comprehensive Collection\n\n")
            
            for domain in sorted(domains):
                f.write(f"0.0.0.0 {domain}\n")
        
        logger.info(f"Generated Pi-Hole format: {output_path} ({len(domains)} domains)")
    
    def generate_domain_list(self, domains, filename):
        """Generate plain domain list."""
        output_path = os.path.join(self.output_dir, filename)
        
        with open(output_path, 'w') as f:
            f.write(f"# Domain List - {filename}\n")
            f.write(f"# Generated: {datetime.now().isoformat()}\n")
            f.write(f"# Total domains: {len(domains)}\n")
            f.write(f"# Source: Blockage Comprehensive Collection\n\n")
            
            for domain in sorted(domains):
                f.write(f"{domain}\n")
        
        logger.info(f"Generated domain list: {output_path} ({len(domains)} domains)")
    
    def generate_statistics(self):
        """Generate and save statistics."""
        stats = {
            'generation_time': datetime.now().isoformat(),
            'total_domains': len(self.all_domains),
            'categories': {cat: len(domains) for cat, domains in self.domains.items()},
            'top_domains': dict(Counter(self.all_domains).most_common(20)),
            'statistics': dict(self.statistics)
        }
        
        stats_path = os.path.join(self.output_dir, 'statistics.json')
        with open(stats_path, 'w') as f:
            json.dump(stats, f, indent=2)
        
        logger.info(f"Generated statistics: {stats_path}")
        
        # Also create a human-readable report
        report_path = os.path.join(self.output_dir, 'report.txt')
        with open(report_path, 'w') as f:
            f.write("Blockage Comprehensive Blocklist Report\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"Generated: {stats['generation_time']}\n")
            f.write(f"Total unique domains: {stats['total_domains']:,}\n\n")
            
            f.write("Domains by category:\n")
            for cat, count in sorted(stats['categories'].items()):
                f.write(f"  {cat}: {count:,}\n")
            
            f.write(f"\nDownload statistics:\n")
            f.write(f"  Successful: {self.statistics.get('downloads_successful', 0)}\n")
            f.write(f"  Failed: {self.statistics.get('downloads_failed', 0)}\n")
        
        logger.info(f"Generated report: {report_path}")
    
    def run(self, categories=None, output_formats=None):
        """Run the complete aggregation process."""
        if output_formats is None:
            output_formats = ['pihole', 'domains']
        
        logger.info("Starting Blockage Comprehensive Blocklist Aggregation")
        
        # Load whitelist
        self.load_whitelist()
        
        # Aggregate all lists
        self.aggregate_all_lists(categories)
        
        # Generate output files
        if 'pihole' in output_formats:
            self.generate_pihole_format(self.all_domains, 'blocklist_comprehensive.txt')
            
            # Generate category-specific files
            for category, domains in self.domains.items():
                if domains:
                    self.generate_pihole_format(domains, f'blocklist_{category}.txt')
        
        if 'domains' in output_formats:
            self.generate_domain_list(self.all_domains, 'domains_comprehensive.txt')
            
            # Generate category-specific files
            for category, domains in self.domains.items():
                if domains:
                    self.generate_domain_list(domains, f'domains_{category}.txt')
        
        # Generate statistics
        self.generate_statistics()
        
        logger.info("Aggregation complete!")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Comprehensive Pi-Hole Blocklist Aggregator')
    parser.add_argument('--categories', nargs='+', help='Specific categories to process')
    parser.add_argument('--output-dir', default='output', help='Output directory')
    parser.add_argument('--config', default='blocklist_sources.json', help='Configuration file')
    parser.add_argument('--formats', nargs='+', choices=['pihole', 'domains'], 
                       default=['pihole', 'domains'], help='Output formats')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    aggregator = BlocklistAggregator(args.config, args.output_dir)
    aggregator.run(args.categories, args.formats)


if __name__ == '__main__':
    main()