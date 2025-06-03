#!/usr/bin/env python3
"""
Quick test script for CeWL functionality in ipsnipe
"""

import os
import sys
import tempfile

# Add the parent directory to the path so we can import ipsnipe modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ipsnipe.scanners.wordlist_manager import WordlistManager

def test_cewl_functionality():
    """Test CeWL functionality with improved error handling"""
    print("🧪 Testing CeWL functionality...")
    
    # Create temporary output directory
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 Using temp directory: {temp_dir}")
        
        # Initialize WordlistManager
        config = {'wordlists': {}}
        wm = WordlistManager(config, temp_dir)
        
        # Test 1: Check CeWL availability
        print("\n1️⃣  Testing CeWL availability...")
        cewl_available = wm.check_cewl_available()
        print(f"   CeWL available: {cewl_available}")
        
        # Test 2: Run diagnostics
        print("\n2️⃣  Running CeWL diagnostics...")
        test_url = "https://www.example.com"
        diagnostics = wm.diagnose_cewl_issues(test_url)
        
        # Test 3: Test URL selection logic
        print("\n3️⃣  Testing URL selection logic...")
        wm.set_discovered_domains(["example.com", "test.local"])
        wm.set_web_ports([80, 443, 8080])
        
        best_url = wm._get_best_cewl_target()
        print(f"   Best URL selected: {best_url}")
        
        # Test 4: Try CeWL generation if available
        if cewl_available and best_url:
            print("\n4️⃣  Testing CeWL wordlist generation...")
            result = wm.generate_cewl_wordlist(
                target_url=best_url,
                depth=1,  # Shallow depth for quick test
                min_word_length=4,
                max_word_length=10
            )
            print(f"   CeWL result: {result}")
            
            if result and os.path.exists(result):
                print(f"   ✅ Wordlist created: {result}")
                with open(result, 'r') as f:
                    lines = f.readlines()
                    print(f"   📊 Lines in wordlist: {len(lines)}")
                    if lines:
                        print(f"   📄 First few words: {lines[:5]}")
            else:
                print(f"   ❌ CeWL generation failed")
        else:
            print(f"\n4️⃣  Skipping CeWL generation test (not available or no URL)")
        
        print(f"\n✅ CeWL test complete!")

if __name__ == "__main__":
    test_cewl_functionality() 