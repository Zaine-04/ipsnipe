#!/usr/bin/env python3
"""
Streamlined report generation for ipsnipe
Creates concise, actionable reports focused on key findings
"""

import datetime
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from ..ui.colors import Colors


class ReportGenerator:
    """Generate streamlined, actionable reports"""
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
    
    def generate_summary_report(self, target_ip: str, results: Dict, open_ports: List[int], 
                               web_ports: List[int], domains: List[str] = None):
        """Generate concise summary report focused on actionable findings"""
        findings_file = Path(self.output_dir) / "FINDINGS.md"
        summary_file = Path(self.output_dir) / "SUMMARY.md"
        
        # Extract key findings from all scans
        key_findings = self._extract_actionable_findings(results)
        
        # Generate focused findings report (primary report)
        self._generate_findings_report(findings_file, target_ip, key_findings, open_ports, web_ports, domains)
        
        # Generate brief summary
        self._generate_brief_summary(summary_file, target_ip, results, open_ports, web_ports, domains)
        
        print(f"{Colors.GREEN}🎯 Key findings: {findings_file}{Colors.END}")
        print(f"{Colors.GREEN}📊 Brief summary: {summary_file}{Colors.END}")
    
    def _extract_actionable_findings(self, results: Dict) -> Dict[str, List[str]]:
        """Extract only actionable findings from scan results"""
        findings = {
            'critical_vulns': [],
            'open_services': [],
            'web_paths': [],
            'interesting_files': [],
            'technologies': [],
            'credentials': [],
            'emails': [],
            'subdomains': []
        }
        
        for scan_name, result in results.items():
            if result.get('status') != 'success':
                continue
                
            output_file = result.get('output_file')
            if not output_file or not Path(output_file).exists():
                continue
                
            try:
                with open(output_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Extract findings based on scan type
                if 'nmap' in scan_name:
                    findings['open_services'].extend(self._extract_services(content))
                elif any(x in scan_name for x in ['gobuster', 'ferox', 'ffuf']):
                    paths, files = self._extract_web_content(content)
                    findings['web_paths'].extend(paths)
                    findings['interesting_files'].extend(files)
                elif 'nikto' in scan_name:
                    findings['critical_vulns'].extend(self._extract_vulns(content))
                elif 'whatweb' in scan_name:
                    findings['technologies'].extend(self._extract_tech_stack(content))
                elif 'theharvester' in scan_name:
                    findings['emails'].extend(self._extract_emails(content))
                    findings['subdomains'].extend(self._extract_subdomains(content))
                elif 'dnsrecon' in scan_name:
                    findings['subdomains'].extend(self._extract_dns_records(content))
                
                # Always look for credentials
                findings['credentials'].extend(self._find_credentials(content))
                
            except Exception:
                continue
        
        # Clean and deduplicate
        for key in findings:
            findings[key] = sorted(list(set(filter(None, findings[key]))))
        
        return findings
    
    def _extract_services(self, content: str) -> List[str]:
        """Extract open services from nmap output"""
        services = []
        for line in content.split('\n'):
            # Match nmap service lines
            match = re.search(r'(\d+)/(tcp|udp)\s+open\s+([^\s]+)(?:\s+(.+))?', line)
            if match:
                port, proto, service, version = match.groups()
                if version and version.strip():
                    services.append(f"{port}/{proto} {service} ({version.strip()})")
                else:
                    services.append(f"{port}/{proto} {service}")
        return services
    
    def _extract_web_content(self, content: str) -> Tuple[List[str], List[str]]:
        """Extract web directories and interesting files"""
        paths = []
        files = []
        
        interesting_extensions = ['.php', '.asp', '.aspx', '.jsp', '.txt', '.xml', '.config', '.bak', '.sql', '.log']
        admin_keywords = ['admin', 'login', 'dashboard', 'panel', 'config', 'backup', 'upload']
        
        for line in content.split('\n'):
            # Extract paths from common formats
            path = None
            if line.startswith('/') and any(status in line for status in ['200', '301', '302']):
                path = line.split()[0]
            elif 'Status:' in line and any(status in line for status in ['200', '301']):
                match = re.search(r'https?://[^/]+(/[^\s]+)', line)
                if match:
                    path = match.group(1)
            
            if path:
                # Categorize as file or directory
                if any(path.endswith(ext) for ext in interesting_extensions):
                    files.append(path)
                elif any(keyword in path.lower() for keyword in admin_keywords):
                    paths.append(f"{path} [ADMIN]")
                elif path != '/':
                    paths.append(path)
        
        return paths[:20], files[:15]  # Limit results
    
    def _extract_vulns(self, content: str) -> List[str]:
        """Extract critical vulnerabilities from Nikto output"""
        vulns = []
        for line in content.split('\n'):
            if line.startswith('+') and any(keyword in line.lower() for keyword in 
                                          ['vuln', 'cve', 'security', 'exploit', 'injection']):
                # Clean up the line
                clean_line = re.sub(r'^\+\s*', '', line).strip()
                if len(clean_line) > 20:  # Filter out very short findings
                    vulns.append(clean_line)
        return vulns[:10]  # Top 10
    
    def _extract_tech_stack(self, content: str) -> List[str]:
        """Extract technology stack from WhatWeb output"""
        technologies = []
        
        # Common patterns for technology detection
        tech_patterns = [
            r'([A-Za-z-]+)\s+\[([^\]]+)\]',  # Apache [2.4.41]
            r'([A-Za-z-]+)\s+(\d+\.\d+[\.\d]*)',  # PHP 7.4.3
        ]
        
        for pattern in tech_patterns:
            for match in re.finditer(pattern, content):
                tech, version = match.groups()
                if tech.lower() in ['apache', 'nginx', 'php', 'mysql', 'wordpress', 'drupal', 'joomla']:
                    technologies.append(f"{tech} {version}")
        
        return technologies[:8]  # Limit to key technologies
    
    def _extract_emails(self, content: str) -> List[str]:
        """Extract email addresses"""
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(pattern, content)
        return [email for email in emails if not email.endswith(('.png', '.jpg', '.gif'))][:10]
    
    def _extract_subdomains(self, content: str) -> List[str]:
        """Extract subdomains from theHarvester output"""
        subdomains = []
        for line in content.split('\n'):
            # Look for domain patterns
            match = re.search(r'([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', line)
            if match and '.' in match.group(1) and not '@' in line:
                subdomain = match.group(1).lower()
                if subdomain.count('.') >= 1:
                    subdomains.append(subdomain)
        return subdomains[:10]
    
    def _extract_dns_records(self, content: str) -> List[str]:
        """Extract DNS records from dnsrecon"""
        records = []
        for line in content.split('\n'):
            if any(record_type in line for record_type in ['A ', 'CNAME', 'MX', 'TXT']):
                match = re.search(r'([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', line)
                if match:
                    records.append(match.group(1).lower())
        return records[:10]
    
    def _find_credentials(self, content: str) -> List[str]:
        """Look for potential credentials in any scan output"""
        credentials = []
        patterns = [
            r'password[:\s=]+([^\s\n]{3,})',
            r'username[:\s=]+([^\s\n]{3,})',
            r'admin[:\s=]+([^\s\n]{3,})',
            r'login[:\s=]+([^\s\n]{3,})',
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                cred = match.group(1)
                if len(cred) > 3 and cred.lower() not in ['password', 'username', 'admin', 'login']:
                    credentials.append(f"{match.group(0)}")
        
        return credentials[:5]
    
    def _generate_findings_report(self, file_path: Path, target_ip: str, findings: Dict[str, List[str]], 
                                 open_ports: List[int], web_ports: List[int], domains: List[str] = None):
        """Generate the main findings report"""
        with open(file_path, 'w') as f:
            f.write(f"# 🎯 HTB FINDINGS: {target_ip}\n\n")
            if domains:
                f.write(f"**Domains:** {', '.join(domains)}\n\n")
            
            # Critical findings first
            if findings['critical_vulns']:
                f.write("## 🚨 CRITICAL VULNERABILITIES\n\n")
                for vuln in findings['critical_vulns']:
                    f.write(f"- {vuln}\n")
                f.write("\n")
            
            if findings['credentials']:
                f.write("## 🔑 POTENTIAL CREDENTIALS\n\n")
                for cred in findings['credentials']:
                    f.write(f"- {cred}\n")
                f.write("\n")
            
            # Network services
            if findings['open_services']:
                f.write("## 🌐 OPEN SERVICES\n\n")
                for service in findings['open_services']:
                    f.write(f"- {service}\n")
                f.write("\n")
            
            # Web findings
            if findings['web_paths'] or findings['interesting_files']:
                f.write("## 🌐 WEB FINDINGS\n\n")
                
                if findings['interesting_files']:
                    f.write("### 📄 Interesting Files\n")
                    for file in findings['interesting_files']:
                        f.write(f"- {file}\n")
                    f.write("\n")
                
                if findings['web_paths']:
                    f.write("### 📁 Discovered Paths\n")
                    for path in findings['web_paths']:
                        f.write(f"- {path}\n")
                    f.write("\n")
            
            # Technology stack
            if findings['technologies']:
                f.write("## 🔧 TECHNOLOGY STACK\n\n")
                for tech in findings['technologies']:
                    f.write(f"- {tech}\n")
                f.write("\n")
            
            # Additional intel
            if findings['emails'] or findings['subdomains']:
                f.write("## 📧 ADDITIONAL INTEL\n\n")
                
                if findings['emails']:
                    f.write("### Email Addresses\n")
                    for email in findings['emails']:
                        f.write(f"- {email}\n")
                    f.write("\n")
                
                if findings['subdomains']:
                    f.write("### Subdomains\n")
                    for subdomain in findings['subdomains']:
                        f.write(f"- {subdomain}\n")
                    f.write("\n")
            
            # Next steps
            f.write("## 📋 NEXT STEPS\n\n")
            if findings['critical_vulns']:
                f.write("1. **Investigate vulnerabilities** - Test critical findings\n")
            if findings['credentials']:
                f.write("2. **Test credentials** - Try discovered login info\n")
            if findings['interesting_files']:
                f.write("3. **Check files** - Browse interesting files manually\n")
            if findings['web_paths']:
                f.write("4. **Explore paths** - Manual inspection of web directories\n")
            if findings['technologies']:
                f.write("5. **Research CVEs** - Look up vulnerabilities for detected versions\n")
    
    def _generate_brief_summary(self, file_path: Path, target_ip: str, results: Dict, 
                               open_ports: List[int], web_ports: List[int], domains: List[str] = None):
        """Generate a brief summary of the scan session"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        successful_scans = [scan for scan, result in results.items() if result.get('status') == 'success']
        failed_scans = [scan for scan, result in results.items() if result.get('status') == 'failed']
        
        with open(file_path, 'w') as f:
            f.write(f"# SCAN SUMMARY: {target_ip}\n\n")
            f.write(f"**Date:** {timestamp}\n")
            if domains:
                f.write(f"**Domains:** {', '.join(domains)}\n")
            f.write(f"**Successful Scans:** {len(successful_scans)}\n")
            f.write(f"**Failed Scans:** {len(failed_scans)}\n\n")
            
            f.write(f"**Open Ports:** {len(open_ports)} ({', '.join(map(str, open_ports[:10]))}{'...' if len(open_ports) > 10 else ''})\n")
            f.write(f"**Web Services:** {len(web_ports)} ({', '.join(map(str, web_ports))})\n\n")
            
            if successful_scans:
                f.write("## ✅ Completed Scans\n")
                for scan in successful_scans:
                    f.write(f"- {scan.replace('_', ' ').title()}\n")
                f.write("\n")
            
            if failed_scans:
                f.write("## ❌ Failed Scans\n")
                for scan in failed_scans:
                    f.write(f"- {scan.replace('_', ' ').title()}\n")
                f.write("\n")
            
            f.write("**📁 Individual scan files contain raw output**\n")
            f.write("**🎯 See FINDINGS.md for actionable results**\n") 