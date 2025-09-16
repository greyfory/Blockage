#!/usr/bin/env python3
"""
Pi-Hole Blocklist Compiler
A comprehensive tool to compile and deduplicate Pi-Hole blocklists from multiple sources.
"""

import requests
import re
import logging
import json
from typing import Set, List, Dict
from urllib.parse import urlparse
import time
from pathlib import Path

class BlocklistCompiler:
    def __init__(self, config_file: str = 'blocklist_sources.json'):
        """Initialize the BlocklistCompiler."""
        self.logger = self._setup_logging()
        self.config_file = config_file
        self.domains: Set[str] = set()
        self.stats = {
            'sources_processed': 0,
            'total_domains_fetched': 0,
            'unique_domains': 0,
            'invalid_domains': 0,
            'failed_sources': 0
        }
        
    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('blocklist_compiler.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def _is_valid_domain(self, domain: str) -> bool:
        """Validate if a string is a valid domain name."""
        if not domain or len(domain) > 253:
            return False
        
        # Remove common prefixes that might be in blocklists
        domain = domain.strip().lower()
        if domain.startswith('0.0.0.0 '):
            domain = domain[8:].strip()
        elif domain.startswith('127.0.0.1 '):
            domain = domain[10:].strip()
        elif domain.startswith('::1 '):
            domain = domain[4:].strip()
        
        # Basic domain validation regex
        domain_pattern = re.compile(
            r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+'
            r'[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?$'
        )
        
        return bool(domain_pattern.match(domain))
    
    def _extract_domains_from_content(self, content: str) -> Set[str]:
        """Extract valid domains from blocklist content."""
        domains = set()
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#') or line.startswith('!'):
                continue
            
            # Handle different blocklist formats
            if line.startswith('0.0.0.0 ') or line.startswith('127.0.0.1 ') or line.startswith('::1 '):
                domain = line.split()[1] if len(line.split()) > 1 else ''
            elif line.startswith('||') and line.endswith('^'):
                # AdBlock format
                domain = line[2:-1]
            else:
                # Assume it's just a domain
                domain = line.split()[0]
            
            if self._is_valid_domain(domain):
                domains.add(domain.lower())
            else:
                self.stats['invalid_domains'] += 1
        
        return domains
    
    def _fetch_blocklist(self, url: str, timeout: int = 30) -> str:
        """Fetch blocklist content from a URL."""
        try:
            headers = {
                'User-Agent': 'Pi-Hole Blocklist Compiler/1.0 (+https://github.com/greyfory/Blockage)'
            }
            response = requests.get(url, timeout=timeout, headers=headers)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch {url}: {e}")
            raise
    
    def load_sources(self) -> List[Dict]:
        """Load blocklist sources from configuration file."""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                return config.get('sources', [])
        except FileNotFoundError:
            self.logger.warning(f"Config file {self.config_file} not found. Using default sources.")
            return self._get_default_sources()
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in config file: {e}")
            return self._get_default_sources()
    
    def _get_default_sources(self) -> List[Dict]:
        """Return a comprehensive list of default Pi-Hole blocklist sources."""
        return [
            {
                "name": "StevenBlack's Unified hosts file",
                "url": "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts",
                "description": "Unified hosts file with base adware + malware"
            },
            {
                "name": "AdGuard DNS filter",
                "url": "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/BaseFilter/sections/adservers.txt",
                "description": "AdGuard Base Filter - ad servers"
            },
            {
                "name": "EasyList",
                "url": "https://easylist.to/easylist/easylist.txt",
                "description": "EasyList filter"
            },
            {
                "name": "Peter Lowe's Ad and tracking server list",
                "url": "https://pgl.yoyo.org/adservers/serverlist.php?hostformat=hosts&showintro=0&mimetype=plaintext",
                "description": "Peter Lowe's blocklist"
            },
            {
                "name": "Dan Pollock's hosts file",
                "url": "https://someonewhocares.org/hosts/zero/hosts",
                "description": "Dan Pollock's hosts file"
            },
            {
                "name": "MVPS hosts file",
                "url": "http://winhelp2002.mvps.org/hosts.txt",
                "description": "MVPS hosts file"
            },
            {
                "name": "Malware Domain List",
                "url": "https://www.malwaredomainlist.com/hostslist/hosts.txt",
                "description": "Malware Domain List"
            },
            {
                "name": "AdAway Default Blocklist",
                "url": "https://raw.githubusercontent.com/AdAway/adaway.github.io/master/hosts.txt",
                "description": "AdAway default blocklist"
            },
            {
                "name": "hpHosts Ad and tracking servers",
                "url": "https://hosts-file.net/ad_servers.txt",
                "description": "hpHosts ad and tracking servers"
            },
            {
                "name": "Disconnect.me Tracking Protection",
                "url": "https://s3.amazonaws.com/lists.disconnect.me/simple_tracking.txt",
                "description": "Disconnect.me tracking protection list"
            },
            {
                "name": "Disconnect.me Ad Protection",
                "url": "https://s3.amazonaws.com/lists.disconnect.me/simple_ad.txt",
                "description": "Disconnect.me ad protection list"
            },
            {
                "name": "NoTracking hosts blocklist",
                "url": "https://raw.githubusercontent.com/notracking/hosts-blocklists/master/hostnames.txt",
                "description": "NoTracking project hosts blocklist"
            },
            {
                "name": "Polish filters for Pi-hole",
                "url": "https://raw.githubusercontent.com/MajkiIT/polish-ads-filter/master/polish-pihole-filters/hostfile.txt",
                "description": "Polish ads and tracking filter"
            },
            {
                "name": "Perflyst and Dandelion Sprout's Smart-TV Blocklist",
                "url": "https://raw.githubusercontent.com/Perflyst/PiHoleBlocklist/master/SmartTV.txt",
                "description": "Smart TV blocklist"
            },
            {
                "name": "Firebog Suspicious Lists",
                "url": "https://v.firebog.net/hosts/static/w3kbl.txt",
                "description": "Firebog suspicious domains"
            }
        ]
    
    def compile_blocklists(self) -> None:
        """Main method to compile all blocklists."""
        sources = self.load_sources()
        total_sources = len(sources)
        
        self.logger.info(f"Starting compilation of {total_sources} blocklist sources...")
        
        for i, source in enumerate(sources, 1):
            name = source.get('name', 'Unknown')
            url = source.get('url', '')
            
            if not url:
                self.logger.warning(f"Skipping source '{name}': No URL provided")
                continue
            
            self.logger.info(f"Processing [{i}/{total_sources}] {name}")
            
            try:
                content = self._fetch_blocklist(url)
                domains = self._extract_domains_from_content(content)
                
                domains_before = len(self.domains)
                self.domains.update(domains)
                domains_after = len(self.domains)
                new_domains = domains_after - domains_before
                
                self.logger.info(f"  - Fetched {len(domains)} domains, {new_domains} new unique domains")
                
                self.stats['sources_processed'] += 1
                self.stats['total_domains_fetched'] += len(domains)
                
                # Add small delay to be respectful to servers
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"  - Failed to process {name}: {e}")
                self.stats['failed_sources'] += 1
        
        self.stats['unique_domains'] = len(self.domains)
        self._log_compilation_stats()
    
    def _log_compilation_stats(self) -> None:
        """Log compilation statistics."""
        self.logger.info("Compilation completed!")
        self.logger.info(f"Sources processed: {self.stats['sources_processed']}")
        self.logger.info(f"Sources failed: {self.stats['failed_sources']}")
        self.logger.info(f"Total domains fetched: {self.stats['total_domains_fetched']}")
        self.logger.info(f"Unique domains: {self.stats['unique_domains']}")
        self.logger.info(f"Invalid domains skipped: {self.stats['invalid_domains']}")
        
        if self.stats['total_domains_fetched'] > 0:
            dedup_ratio = (1 - self.stats['unique_domains'] / self.stats['total_domains_fetched']) * 100
            self.logger.info(f"Deduplication rate: {dedup_ratio:.2f}%")
    
    def save_blocklist(self, output_file: str = 'unified_blocklist.txt') -> None:
        """Save the compiled and deduplicated blocklist to a file."""
        if not self.domains:
            self.logger.warning("No domains to save!")
            return
        
        # Sort domains for consistent output
        sorted_domains = sorted(self.domains)
        
        with open(output_file, 'w') as f:
            # Write header
            f.write("# Unified Pi-Hole Blocklist\n")
            f.write("# Generated by Blockage Pi-Hole Blocklist Compiler\n")
            f.write(f"# Total unique domains: {len(sorted_domains)}\n")
            f.write(f"# Last updated: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}\n")
            f.write("# https://github.com/greyfory/Blockage\n")
            f.write("#\n")
            
            # Write domains
            for domain in sorted_domains:
                f.write(f"{domain}\n")
        
        self.logger.info(f"Blocklist saved to {output_file} with {len(sorted_domains)} unique domains")
    
    def run(self, output_file: str = 'unified_blocklist.txt') -> None:
        """Run the complete compilation process."""
        start_time = time.time()
        
        try:
            self.compile_blocklists()
            self.save_blocklist(output_file)
            
            end_time = time.time()
            self.logger.info(f"Total execution time: {end_time - start_time:.2f} seconds")
            
        except KeyboardInterrupt:
            self.logger.info("Compilation interrupted by user")
        except Exception as e:
            self.logger.error(f"Compilation failed: {e}")
            raise


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Compile Pi-Hole blocklists from multiple sources')
    parser.add_argument('-o', '--output', default='unified_blocklist.txt',
                       help='Output file name (default: unified_blocklist.txt)')
    parser.add_argument('-c', '--config', default='blocklist_sources.json',
                       help='Configuration file (default: blocklist_sources.json)')
    
    args = parser.parse_args()
    
    compiler = BlocklistCompiler(config_file=args.config)
    compiler.run(output_file=args.output)


if __name__ == '__main__':
    main()