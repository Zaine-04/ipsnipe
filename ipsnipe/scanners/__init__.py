#!/usr/bin/env python3
"""
Scanner modules for ipsnipe
Individual scanner implementations
"""

from .nmap_scanner import NmapScanner
from .web_scanners import WebScanners
from .dns_scanner import DNSScanner
from .web_detection import WebDetector
from .param_lfi_scanner import ParameterLFIScanner
from .cms_scanner import CMSScanner
from .wordlist_manager import WordlistManager

# Enhanced scanners (optional imports)
try:
    from .advanced_dns_scanner import AdvancedDNSScanner
    ADVANCED_DNS_AVAILABLE = True
except ImportError:
    ADVANCED_DNS_AVAILABLE = False

try:
    from .enhanced_web_scanner import EnhancedWebScanner
    ENHANCED_WEB_AVAILABLE = True
except ImportError:
    ENHANCED_WEB_AVAILABLE = False

__all__ = [
    'NmapScanner', 'WebScanners', 'DNSScanner', 'WebDetector', 
    'ParameterLFIScanner', 'CMSScanner', 'WordlistManager',
    'ADVANCED_DNS_AVAILABLE', 'ENHANCED_WEB_AVAILABLE'
]

# Conditionally add enhanced scanners if available
if ADVANCED_DNS_AVAILABLE:
    __all__.append('AdvancedDNSScanner')
    
if ENHANCED_WEB_AVAILABLE:
    __all__.append('EnhancedWebScanner') 