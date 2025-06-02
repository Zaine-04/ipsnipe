#!/usr/bin/env python3
"""
Web service detection utility for ipsnipe
Provides fallback web service detection when nmap fails to identify them
"""

import subprocess
import re
from typing import List, Dict, Tuple
from ..ui.colors import Colors


class WebDetector:
    """Standalone web service detector"""
    
    def __init__(self):
        self.common_web_ports = [80, 443, 8080, 8443, 8000, 8888, 9000, 3000, 5000, 8008, 8181, 9090]
    
    def test_http_response(self, target_ip: str, port: int, protocol: str = 'http', timeout: int = 5) -> Dict:
        """Test if a port responds to HTTP/HTTPS requests"""
        url = f"{protocol}://{target_ip}:{port}"
        
        try:
            # Use curl to test responsiveness
            curl_args = [
                'curl', '-s', '-I', '--max-time', str(timeout), '--connect-timeout', '3',
                '--user-agent', 'ipsnipe/2.1 (Security Scanner)'
            ]
            
            if protocol == 'https':
                curl_args.append('-k')  # Allow insecure SSL
            
            curl_args.append(url)
            
            result = subprocess.run(curl_args, capture_output=True, text=True, timeout=timeout + 2)
            
            if result.returncode == 0 and result.stdout:
                # Parse HTTP response
                response_info = self._parse_http_response(result.stdout)
                response_info.update({
                    'responsive': True,
                    'url': url,
                    'protocol': protocol,
                    'port': port
                })
                return response_info
                
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, Exception) as e:
            pass
        
        return {'responsive': False, 'port': port, 'protocol': protocol, 'error': str(e) if 'e' in locals() else 'No response'}
    
    def _parse_http_response(self, response_text: str) -> Dict:
        """Parse HTTP response headers for useful information"""
        info = {
            'status_code': 0,
            'server': 'Unknown',
            'headers': {},
            'technologies': []
        }
        
        lines = response_text.strip().split('\n')
        
        # Parse status line
        if lines:
            status_match = re.search(r'HTTP/\d+\.?\d*\s+(\d{3})', lines[0])
            if status_match:
                info['status_code'] = int(status_match.group(1))
        
        # Parse headers
        for line in lines[1:]:
            if ':' in line:
                key, value = line.split(':', 1)
                header_name = key.strip().lower()
                header_value = value.strip()
                info['headers'][header_name] = header_value
                
                # Extract server information
                if header_name == 'server':
                    info['server'] = header_value
                
                # Detect technologies
                if header_name in ['x-powered-by', 'x-aspnet-version', 'x-generator']:
                    info['technologies'].append(f"{header_name}: {header_value}")
        
        return info
    
    def scan_common_web_ports(self, target_ip: str, open_ports: List[int] = None) -> List[Dict]:
        """Scan common web ports for HTTP/HTTPS services"""
        print(f"{Colors.YELLOW}🔍 Scanning for web services on common ports...{Colors.END}")
        
        # Use provided open ports or scan common web ports
        ports_to_test = open_ports if open_ports else self.common_web_ports
        
        web_services = []
        
        for port in ports_to_test:
            if open_ports and port not in open_ports:
                continue
                
            print(f"{Colors.CYAN}   Testing port {port}...{Colors.END}")
            
            # Test HTTP first
            http_result = self.test_http_response(target_ip, port, 'http', timeout=3)
            if http_result['responsive']:
                web_services.append(http_result)
                print(f"{Colors.GREEN}   ✅ HTTP service on port {port} - {http_result['status_code']} ({http_result['server']}){Colors.END}")
                continue
            
            # Test HTTPS if HTTP failed
            https_result = self.test_http_response(target_ip, port, 'https', timeout=3)
            if https_result['responsive']:
                web_services.append(https_result)
                print(f"{Colors.GREEN}   ✅ HTTPS service on port {port} - {https_result['status_code']} ({https_result['server']}){Colors.END}")
                continue
            
            # Only show failure for common web ports
            if port in [80, 443, 8080, 8443]:
                print(f"{Colors.YELLOW}   ❌ No web service on port {port}{Colors.END}")
        
        if web_services:
            print(f"{Colors.GREEN}🌐 Found {len(web_services)} web service(s){Colors.END}")
        else:
            print(f"{Colors.YELLOW}⚠️  No web services detected on tested ports{Colors.END}")
        
        return web_services
    
    def get_best_web_target(self, web_services: List[Dict]) -> Tuple[str, Dict]:
        """Get the best web service target from detected services"""
        if not web_services:
            return None, None
        
        # Priority: HTTPS > HTTP, lower port numbers preferred, 200 status preferred
        def service_priority(service):
            protocol_priority = 0 if service['protocol'] == 'https' else 1
            port_priority = service['port']
            status_priority = 0 if service['status_code'] == 200 else 1
            return (protocol_priority, status_priority, port_priority)
        
        best_service = min(web_services, key=service_priority)
        return best_service['url'], best_service
    
    def detect_web_technologies(self, target_ip: str, web_services: List[Dict]) -> Dict:
        """Detect web technologies from discovered services"""
        technologies = set()
        
        for service in web_services:
            # Add server information
            if service.get('server') and service['server'] != 'Unknown':
                technologies.add(f"Server: {service['server']}")
            
            # Add detected technologies
            for tech in service.get('technologies', []):
                technologies.add(tech)
        
        return {
            'technologies': list(technologies),
            'web_services': web_services
        }
    
    def quick_web_check(self, target_ip: str, open_ports: List[int] = None) -> Dict:
        """Quick check for web services with basic technology detection"""
        web_services = self.scan_common_web_ports(target_ip, open_ports)
        
        if not web_services:
            return {
                'has_web_services': False,
                'web_ports': [],
                'services': [],
                'technologies': []
            }
        
        web_ports = [service['port'] for service in web_services]
        tech_info = self.detect_web_technologies(target_ip, web_services)
        
        return {
            'has_web_services': True,
            'web_ports': web_ports,
            'services': web_services,
            'technologies': tech_info['technologies'],
            'best_target': self.get_best_web_target(web_services)
        } 