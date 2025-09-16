#!/usr/bin/env python3
"""
Blockage Validation Script
Tests the blocklist aggregator functionality
"""

import os
import sys
import json
import subprocess

def test_basic_functionality():
    """Test basic aggregator functionality with a minimal run."""
    print("🧪 Testing basic functionality...")
    
    # Test with just one category to avoid long downloads
    cmd = [
        sys.executable, 'blocklist_aggregator.py',
        '--categories', 'advertising',
        '--output-dir', 'validation_test',
        '--formats', 'pihole'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode != 0:
            print(f"❌ Aggregator failed: {result.stderr}")
            return False
            
        # Check if output files were created
        expected_files = [
            'validation_test/blocklist_comprehensive.txt',
            'validation_test/blocklist_advertising.txt',
            'validation_test/statistics.json',
            'validation_test/report.txt'
        ]
        
        for file_path in expected_files:
            if not os.path.exists(file_path):
                print(f"❌ Missing expected file: {file_path}")
                return False
            
            # Check if file has content
            if os.path.getsize(file_path) == 0:
                print(f"❌ Empty file: {file_path}")
                return False
        
        # Validate statistics
        with open('validation_test/statistics.json') as f:
            stats = json.load(f)
            
        if stats['total_domains'] == 0:
            print("❌ No domains were processed")
            return False
            
        print(f"✅ Successfully processed {stats['total_domains']} domains")
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ Test timed out")
        return False
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

def test_configuration_loading():
    """Test configuration file loading."""
    print("🧪 Testing configuration loading...")
    
    if not os.path.exists('blocklist_sources.json'):
        print("❌ Configuration file not found")
        return False
    
    try:
        with open('blocklist_sources.json') as f:
            config = json.load(f)
        
        required_keys = ['metadata', 'blocklist_sources']
        for key in required_keys:
            if key not in config:
                print(f"❌ Missing required configuration key: {key}")
                return False
        
        # Check if we have blocklist sources
        if not config['blocklist_sources']:
            print("❌ No blocklist sources configured")
            return False
        
        print(f"✅ Configuration valid with {len(config['blocklist_sources'])} categories")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in configuration: {e}")
        return False
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_whitelist_loading():
    """Test whitelist file loading."""
    print("🧪 Testing whitelist loading...")
    
    if not os.path.exists('whitelist.txt'):
        print("❌ Whitelist file not found")
        return False
    
    try:
        with open('whitelist.txt') as f:
            lines = f.readlines()
        
        # Count non-comment, non-empty lines
        domains = [line.strip() for line in lines 
                  if line.strip() and not line.startswith('#')]
        
        if len(domains) == 0:
            print("⚠️  Whitelist is empty")
        else:
            print(f"✅ Whitelist contains {len(domains)} domains")
        
        return True
        
    except Exception as e:
        print(f"❌ Whitelist test failed: {e}")
        return False

def test_script_permissions():
    """Test that scripts are executable."""
    print("🧪 Testing script permissions...")
    
    scripts = ['blocklist_aggregator.py', 'run_blockage.sh', 'auto_update.sh']
    
    for script in scripts:
        if not os.path.exists(script):
            print(f"❌ Script not found: {script}")
            return False
        
        if not os.access(script, os.X_OK):
            print(f"❌ Script not executable: {script}")
            return False
    
    print("✅ All scripts are executable")
    return True

def cleanup():
    """Clean up test files."""
    import shutil
    if os.path.exists('validation_test'):
        shutil.rmtree('validation_test')

def main():
    """Run all validation tests."""
    print("🛡️  Blockage Validation Suite")
    print("=" * 40)
    
    tests = [
        test_configuration_loading,
        test_whitelist_loading, 
        test_script_permissions,
        test_basic_functionality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Test crashed: {e}")
            print()
    
    # Cleanup
    cleanup()
    
    print("=" * 40)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Blockage is ready to use.")
        print()
        print("Quick start:")
        print("  ./run_blockage.sh --max-protection")
        return True
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)