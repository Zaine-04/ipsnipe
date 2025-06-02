#!/usr/bin/env python3
"""
Demo script for the new skip functionality in ipsnipe
Shows how users can skip individual scans or quit all scans
"""

import sys
import os

# Add the ipsnipe module to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ipsnipe.ui.colors import Colors

def show_skip_feature_demo():
    """Show information about the new skip functionality"""
    
    print(f"{Colors.BOLD}{Colors.GREEN}🎉 ipsnipe New Feature: Interactive Scan Control{Colors.END}")
    print(f"{Colors.CYAN}═══════════════════════════════════════════════════════{Colors.END}\n")
    
    print(f"{Colors.BOLD}⏸️  What's New:{Colors.END}")
    print(f"  {Colors.GREEN}•{Colors.END} Skip individual scans without losing progress")
    print(f"  {Colors.GREEN}•{Colors.END} Quit all remaining scans gracefully")
    print(f"  {Colors.GREEN}•{Colors.END} Real-time scan progress tracking")
    print(f"  {Colors.GREEN}•{Colors.END} Preserve completed scans even when interrupted")
    
    print(f"\n{Colors.BOLD}🎮 How to Use:{Colors.END}")
    print(f"  {Colors.YELLOW}s + Enter{Colors.END} → Skip current scan, continue with next")
    print(f"  {Colors.YELLOW}q + Enter{Colors.END} → Quit all remaining scans gracefully")
    print(f"  {Colors.YELLOW}Ctrl+C{Colors.END}    → Emergency termination (immediate stop)")
    
    print(f"\n{Colors.BOLD}📋 Example Workflow:{Colors.END}")
    print(f"  {Colors.CYAN}1.{Colors.END} Start ipsnipe with multiple scans selected")
    print(f"  {Colors.CYAN}2.{Colors.END} Nmap scan starts - let it complete (finds web services)")
    print(f"  {Colors.CYAN}3.{Colors.END} Directory enumeration starts but is slow")
    print(f"  {Colors.CYAN}4.{Colors.END} Press 's' + Enter to skip to vulnerability scan")
    print(f"  {Colors.CYAN}5.{Colors.END} Nikto finds interesting results")
    print(f"  {Colors.CYAN}6.{Colors.END} Press 'q' + Enter to quit remaining scans")
    print(f"  {Colors.CYAN}7.{Colors.END} All completed scans are saved and summarized")
    
    print(f"\n{Colors.BOLD}💡 Benefits:{Colors.END}")
    print(f"  {Colors.GREEN}✅{Colors.END} No more waiting for slow scans you don't need")
    print(f"  {Colors.GREEN}✅{Colors.END} Adapt strategy based on early findings")
    print(f"  {Colors.GREEN}✅{Colors.END} Save time while preserving useful results")
    print(f"  {Colors.GREEN}✅{Colors.END} Better workflow for CTF competitions")
    
    print(f"\n{Colors.BOLD}🔧 Technical Implementation:{Colors.END}")
    print(f"  {Colors.BLUE}•{Colors.END} Threading-based input monitoring")
    print(f"  {Colors.BLUE}•{Colors.END} Graceful process termination")
    print(f"  {Colors.BLUE}•{Colors.END} Proper cleanup and resource management")
    print(f"  {Colors.BLUE}•{Colors.END} Cross-platform compatibility")
    
    print(f"\n{Colors.BOLD}🧪 Testing:{Colors.END}")
    print(f"  Run {Colors.YELLOW}python3 test_skip_functionality.py{Colors.END} to test with mock scans")
    
    print(f"\n{Colors.BOLD}🚀 Try it now:{Colors.END}")
    print(f"  {Colors.CYAN}python3 ipsnipe.py{Colors.END}")
    print(f"  Select multiple scans and test the skip functionality!")
    
    print(f"\n{Colors.GREEN}🎯 This feature makes ipsnipe even better for efficient reconnaissance!{Colors.END}")

def show_usage_examples():
    """Show practical usage examples"""
    
    print(f"\n{Colors.BOLD}{Colors.PURPLE}📚 Practical Usage Examples{Colors.END}")
    print(f"{Colors.PURPLE}═══════════════════════════════════{Colors.END}\n")
    
    examples = [
        {
            'scenario': 'HTB Machine - Quick Win Strategy',
            'description': 'Find quick wins without waiting for exhaustive scans',
            'steps': [
                'Start with: Nmap Quick + Directory Enum + Nikto + WhatWeb',
                'Let Nmap complete to find web services',
                'If directory enum is slow and Nmap found interesting ports, skip it',
                'Let Nikto run for vulnerability detection', 
                'Skip remaining scans if you found an exploit path'
            ]
        },
        {
            'scenario': 'Time-Constrained Pentest',
            'description': 'Maximize information gathering in limited time',
            'steps': [
                'Select all scans for comprehensive coverage',
                'Monitor progress and skip scans that aren\'t productive',
                'Focus on scans that are finding results',
                'Use quit function when you have enough info to proceed'
            ]
        },
        {
            'scenario': 'Debugging/Development',
            'description': 'Test specific scan combinations quickly',
            'steps': [
                'Select multiple scans to test',
                'Skip scans that aren\'t relevant to current testing',
                'Iterate quickly through different scan combinations',
                'Verify scan results and reporting functionality'
            ]
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"{Colors.BOLD}{Colors.BLUE}Example {i}: {example['scenario']}{Colors.END}")
        print(f"{Colors.CYAN}{example['description']}{Colors.END}")
        print(f"{Colors.BOLD}Steps:{Colors.END}")
        for step in example['steps']:
            print(f"  {Colors.YELLOW}•{Colors.END} {step}")
        print()

if __name__ == "__main__":
    show_skip_feature_demo()
    show_usage_examples()
    
    print(f"\n{Colors.BOLD}{Colors.GREEN}Ready to try the new skip functionality? 🚀{Colors.END}")
    print(f"{Colors.CYAN}Run: python3 ipsnipe.py{Colors.END}") 