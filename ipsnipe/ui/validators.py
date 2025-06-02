#!/usr/bin/env python3
"""
Input validation utilities for ipsnipe
Handles IP address, port range, and other input validation
"""

import ipaddress
import re


class Validators:
    """Input validation utilities"""
    
    @staticmethod
    def validate_ip(ip_string: str) -> bool:
        """Validate if string is a valid IP address"""
        try:
            ipaddress.ip_address(ip_string)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_port_range(port_range: str) -> bool:
        """Validate port range format (e.g., 80, 80-443, 80,443,8080)"""
        if not port_range or port_range.strip() == "":
            return False
        
        # Remove whitespace
        port_range = port_range.replace(" ", "")
        
        # Split on commas for multiple port specifications
        port_specs = port_range.split(',')
        
        for spec in port_specs:
            # Check if it's a range (e.g., 80-443)
            if '-' in spec:
                parts = spec.split('-')
                if len(parts) != 2:
                    return False
                try:
                    start_port = int(parts[0])
                    end_port = int(parts[1])
                    if not (1 <= start_port <= 65535) or not (1 <= end_port <= 65535):
                        return False
                    if start_port >= end_port:
                        return False
                except ValueError:
                    return False
            else:
                # Single port
                try:
                    port = int(spec)
                    if not (1 <= port <= 65535):
                        return False
                except ValueError:
                    return False
        
        return True
    
    @staticmethod
    def validate_domain(domain: str) -> bool:
        """Basic domain name validation"""
        if not domain:
            return False
        
        # Simple regex for domain validation
        domain_pattern = re.compile(
            r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+'
            r'[a-zA-Z]{2,}$'
        )
        
        return bool(domain_pattern.match(domain))
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Basic URL validation"""
        if not url:
            return False
        
        # Simple URL pattern
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}'  # domain
            r'(?::\d+)?'  # optional port
            r'(?:/.*)?$'  # optional path
        )
        
        return bool(url_pattern.match(url))
    
    @staticmethod
    def normalize_port_range(port_range: str) -> str:
        """Normalize port range string (remove spaces, etc.)"""
        if not port_range:
            return ""
        return port_range.replace(" ", "")
    
    @staticmethod
    def expand_port_range(port_range: str) -> list:
        """Expand port range string to list of individual ports"""
        if not Validators.validate_port_range(port_range):
            return []
        
        ports = []
        port_specs = port_range.replace(" ", "").split(',')
        
        for spec in port_specs:
            if '-' in spec:
                start, end = map(int, spec.split('-'))
                ports.extend(range(start, end + 1))
            else:
                ports.append(int(spec))
        
        return sorted(list(set(ports)))  # Remove duplicates and sort 