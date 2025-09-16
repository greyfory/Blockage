#!/usr/bin/env python3
"""
Example usage of the Blockage Pi-Hole Blocklist Compiler

This script demonstrates how to use the compiler programmatically.
For command-line usage, use: python blocklist_compiler.py
"""

from blocklist_compiler import BlocklistCompiler
import json

def create_custom_config():
    """Create a custom configuration with a subset of fast, reliable sources."""
    
    config = {
        "sources": [
            {
                "name": "AdAway Default Blocklist",
                "url": "https://raw.githubusercontent.com/AdAway/adaway.github.io/master/hosts.txt",
                "description": "AdAway default blocklist - mobile ad blocking",
                "enabled": True
            },
            {
                "name": "StevenBlack's Unified hosts file",
                "url": "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts",
                "description": "Unified hosts file with base adware + malware",
                "enabled": True
            },
            {
                "name": "NextDNS CNAME Cloaking List",
                "url": "https://raw.githubusercontent.com/nextdns/cname-cloaking-blocklist/master/domains",
                "description": "CNAME cloaking domains",
                "enabled": True
            }
        ],
        "settings": {
            "timeout": 30,
            "delay_between_requests": 1
        }
    }
    
    with open('example_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    return 'example_config.json'

def main():
    """Example of programmatic usage."""
    
    print("🔥 Blockage Pi-Hole Blocklist Compiler - Example Usage")
    print("=" * 60)
    
    # Option 1: Use default configuration
    print("\n📖 Option 1: Using default configuration (20+ sources)")
    print("   compiler = BlocklistCompiler()")
    print("   compiler.run('my_blocklist.txt')")
    
    # Option 2: Use custom configuration  
    print("\n📖 Option 2: Using custom configuration")
    config_file = create_custom_config()
    print(f"   config_file = create_custom_config()  # Creates {config_file}")
    print("   compiler = BlocklistCompiler(config_file)")
    print("   compiler.run('custom_blocklist.txt')")
    
    # Option 3: Step by step
    print("\n📖 Option 3: Step-by-step compilation")
    print("   compiler = BlocklistCompiler()")
    print("   compiler.compile_blocklists()  # Download and process")
    print("   compiler.save_blocklist('output.txt')  # Save results")
    
    # Show what the config looks like
    print(f"\n📄 Example custom configuration ({config_file}):")
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    print(f"   Sources: {len(config['sources'])}")
    for i, source in enumerate(config['sources'], 1):
        print(f"   {i}. {source['name']}")
    
    print("\n🚀 To run the full compiler with all sources:")
    print("   python blocklist_compiler.py")
    
    print("\n🚀 To run with custom output file:")
    print("   python blocklist_compiler.py -o my_custom_blocklist.txt")
    
    print("\n🚀 To run with custom config:")
    print(f"   python blocklist_compiler.py -c {config_file} -o custom_output.txt")
    
    print("\n📝 Output will be a text file with one domain per line, suitable for Pi-Hole.")
    
    # Cleanup
    import os
    try:
        os.remove(config_file)
    except:
        pass

if __name__ == '__main__':
    main()