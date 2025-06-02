#!/usr/bin/env python3
"""
Core scanner functionality for ipsnipe
Handles command execution, output formatting, and result processing
"""

import subprocess
import time
import datetime
import re
import textwrap
import threading
import queue
import signal
import sys
import os
from pathlib import Path
from typing import Dict, List
from ..ui.colors import Colors
from ..ui.progress import ScanProgressIndicator


class ScannerCore:
    """Core scanning functionality and command execution"""
    
    def __init__(self, config: Dict, output_dir: str):
        self.config = config
        self.output_dir = output_dir
        self.skip_current_scan = False
        self.current_process = None
        self.input_queue = queue.Queue()
        self.input_thread = None
        self.instructions_shown = False
    
    def start_input_monitor(self):
        """Start monitoring for user input to skip scans"""
        if self.input_thread and self.input_thread.is_alive():
            return
        
        self.input_thread = threading.Thread(target=self._monitor_input, daemon=True)
        self.input_thread.start()
    
    def stop_input_monitor(self):
        """Stop monitoring user input"""
        if self.input_thread and self.input_thread.is_alive():
            # Clear any pending input
            while not self.input_queue.empty():
                try:
                    self.input_queue.get_nowait()
                except queue.Empty:
                    break
    
    def _monitor_input(self):
        """Monitor for user input in a separate thread"""
        try:
            while True:
                user_input = input().strip().lower()
                self.input_queue.put(user_input)
        except (EOFError, KeyboardInterrupt):
            pass
    
    def check_for_skip_request(self) -> bool:
        """Check if user wants to skip current scan"""
        try:
            while not self.input_queue.empty():
                user_input = self.input_queue.get_nowait()
                if user_input in ['s', 'skip']:
                    return True
                elif user_input in ['q', 'quit', 'exit']:
                    return 'quit'
        except queue.Empty:
            pass
        return False
    
    def format_output_content(self, content: str, scan_type: str) -> str:
        """Format and highlight scan output content"""
        if not content.strip():
            return content
        
        lines = content.split('\n')
        formatted_lines = []
        
        for line in lines:
            # Apply highlighting if enabled
            if self.config['output']['highlight_important']:
                line = self.highlight_important_findings(line, scan_type)
            
            # Truncate long lines if enabled
            if self.config['output']['truncate_long_lines']:
                max_length = self.config['output']['max_line_length']
                if len(line) > max_length:
                    line = line[:max_length] + "... [truncated]"
            
            formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    def highlight_important_findings(self, line: str, scan_type: str) -> str:
        """Highlight important findings in scan output"""
        if not line.strip():
            return line
        
        # Common patterns to highlight across all scan types
        common_patterns = [
            (r'\b(open|found|vulnerable|critical|high|medium)\b', Colors.GREEN),
            (r'\b(error|failed|timeout|denied)\b', Colors.RED),
            (r'\b(warning|caution|notice)\b', Colors.YELLOW),
            (r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', Colors.CYAN),  # IP addresses
            (r'\b\d+/tcp\b|\b\d+/udp\b', Colors.BLUE),  # Port numbers
        ]
        
        # Scan-specific patterns
        if scan_type == 'nmap':
            patterns = [
                (r'\b(\d+)/(tcp|udp)\s+(open|closed|filtered)', Colors.GREEN),
                (r'OS details:', Colors.PURPLE),
                (r'Service Info:', Colors.BLUE),
            ]
        elif scan_type in ['feroxbuster', 'ffuf']:
            patterns = [
                (r'Status:\s*(\d+)', Colors.GREEN),
                (r'Size:\s*(\d+)', Colors.CYAN),
                (r'(\.php|\.html|\.txt|\.js|\.css)', Colors.YELLOW),
            ]
        else:
            patterns = []
        
        # Apply highlighting
        all_patterns = common_patterns + patterns
        for pattern, color in all_patterns:
            line = re.sub(pattern, f'{color}\\g<0>{Colors.END}', line, flags=re.IGNORECASE)
        
        return line
    
    def run_command_interruptible(self, command: List[str], output_file: str, description: str, scan_type: str = "generic") -> Dict:
        """Execute a command that can be interrupted by user input"""
        timeout = self.config['general']['scan_timeout']
        
        # Initialize and start progress indicator
        progress = ScanProgressIndicator(description, timeout)
        progress.start()
        
        start_time = time.time()
        
        try:
            # Start the process
            self.current_process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=os.setsid if hasattr(os, 'setsid') else None
            )
            
            # Monitor process while checking for user input and progress indicator status
            while self.current_process.poll() is None:
                # Check if progress indicator detected skip/quit
                if progress.skipped:
                    final_status = progress.stop("skipped")
                    print(f"{Colors.YELLOW}⏭️  Skipping {description} at user request{Colors.END}")
                    self._terminate_process()
                    return self._create_skip_report(output_file, description, start_time)
                elif progress.quit_requested:
                    final_status = progress.stop("quit")
                    print(f"{Colors.YELLOW}🛑 User requested to quit all scans{Colors.END}")
                    self._terminate_process()
                    return {'status': 'user_quit', 'output_file': output_file}
                
                # Check for timeout
                elapsed = time.time() - start_time
                if elapsed > timeout:
                    progress.stop("timeout")
                    print(f"{Colors.RED}⏰ {description} timed out after {timeout//60} minutes{Colors.END}")
                    self._terminate_process()
                    return self._create_timeout_report(output_file, description, timeout)
                
                time.sleep(0.1)  # Small delay to prevent excessive CPU usage
            
            # Process completed normally
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Get output first
            stdout, stderr = self.current_process.communicate()
            return_code = self.current_process.returncode
            
            # Stop progress indicator cleanly
            final_status = progress.stop("completed", execution_time)
            
            # Format the output content
            formatted_stdout = self.format_output_content(stdout, scan_type)
            formatted_stderr = self.format_output_content(stderr, scan_type) if stderr else ""
            
            # Save output to file with better formatting
            output_path = Path(self.output_dir) / output_file
            file_size = self._save_scan_results(
                output_path, description, command, start_time, end_time, 
                execution_time, return_code, formatted_stdout, formatted_stderr
            )
            
            if return_code == 0:
                print(f"{Colors.GREEN}✅ {description} completed successfully ({execution_time:.1f}s, {file_size} bytes){Colors.END}")
                return {
                    'status': 'success',
                    'output_file': str(output_path),
                    'execution_time': execution_time,
                    'file_size': file_size,
                    'return_code': return_code
                }
            else:
                print(f"{Colors.RED}❌ {description} failed with return code {return_code} ({execution_time:.1f}s){Colors.END}")
                return {
                    'status': 'failed',
                    'output_file': str(output_path),
                    'return_code': return_code,
                    'execution_time': execution_time,
                    'file_size': file_size
                }
                
        except FileNotFoundError:
            progress.stop("error")
            print(f"{Colors.RED}❌ Command not found. Please ensure required tools are installed.{Colors.END}")
            return {'status': 'not_found', 'output_file': output_file}
        except Exception as e:
            progress.stop("error")
            print(f"{Colors.RED}❌ Error running {description}: {str(e)}{Colors.END}")
            return {'status': 'error', 'output_file': output_file, 'error': str(e)}
        finally:
            self.current_process = None
    
    def _terminate_process(self):
        """Terminate the current process gracefully"""
        if self.current_process:
            try:
                # Try graceful termination first
                if hasattr(os, 'killpg'):
                    os.killpg(os.getpgid(self.current_process.pid), signal.SIGTERM)
                else:
                    self.current_process.terminate()
                
                # Wait a bit for graceful termination
                try:
                    self.current_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if graceful termination didn't work
                    if hasattr(os, 'killpg'):
                        os.killpg(os.getpgid(self.current_process.pid), signal.SIGKILL)
                    else:
                        self.current_process.kill()
            except (ProcessLookupError, OSError):
                # Process already terminated
                pass
    
    def _create_skip_report(self, output_file: str, description: str, start_time: float) -> Dict:
        """Create a report for a skipped scan"""
        output_path = Path(self.output_dir) / output_file
        skip_time = time.time()
        
        with open(output_path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write(f"ipsnipe Scan Report - {description} (SKIPPED BY USER)\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Status: SKIPPED BY USER REQUEST\n")
            f.write(f"Start Time: {datetime.datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Skip Time: {datetime.datetime.fromtimestamp(skip_time).strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Partial Execution Time: {skip_time - start_time:.2f} seconds\n\n")
            f.write("This scan was manually skipped by the user.\n")
            f.write("No results were generated.\n")
        
        return {
            'status': 'skipped',
            'output_file': str(output_path),
            'reason': 'User requested skip',
            'execution_time': skip_time - start_time
        }
    
    def _create_timeout_report(self, output_file: str, description: str, timeout: int) -> Dict:
        """Create a report for a timed out scan"""
        output_path = Path(self.output_dir) / output_file
        timeout_mins = timeout // 60
        
        with open(output_path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write(f"ipsnipe Scan Report - {description} (TIMEOUT)\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Status: TIMEOUT after {timeout} seconds ({timeout_mins} minutes)\n")
            f.write(f"Timeout Limit: {timeout_mins} minutes\n\n")
            f.write("The scan was terminated due to timeout.\n")
            f.write("Consider:\n")
            f.write("- Increasing timeout in config.toml\n")
            f.write("- Using a smaller wordlist\n")
            f.write("- Reducing scan scope\n")
        
        return {
            'status': 'timeout', 
            'output_file': str(output_path),
            'timeout_duration': timeout
        }
    
    def _save_scan_results(self, output_path: Path, description: str, command: List[str], 
                          start_time: float, end_time: float, execution_time: float, 
                          return_code: int, formatted_stdout: str, formatted_stderr: str) -> int:
        """Save scan results to file in clean format with minimal headers"""
        with open(output_path, 'w') as f:
            # Minimal header for identification only
            f.write(f"# {description}\n")
            f.write(f"# Command: {' '.join(command)}\n")
            f.write(f"# Status: {'SUCCESS' if return_code == 0 else 'FAILED'}\n")
            f.write(f"# Duration: {execution_time:.1f}s\n")
            f.write("#" + "=" * 78 + "\n\n")
            
            # Clean scan output only
            if formatted_stdout:
                # Remove color codes for clean output
                clean_output = re.sub(r'\x1b\[[0-9;]*m', '', formatted_stdout)
                f.write(clean_output)
            else:
                f.write("# No results found\n")
            
            # Add stderr only if there are actual errors (not just warnings)
            if formatted_stderr and ("error" in formatted_stderr.lower() or "failed" in formatted_stderr.lower()):
                f.write(f"\n\n# ERRORS:\n{formatted_stderr}")
        
        return output_path.stat().st_size
    
    def run_command(self, command: List[str], output_file: str, description: str, scan_type: str = "generic") -> Dict:
        """Execute a command and save output with improved formatting - wrapper for backward compatibility"""
        return self.run_command_interruptible(command, output_file, description, scan_type)
    
    def check_dependencies(self) -> bool:
        """Check if required tools are installed"""
        tools = ['nmap', 'whatweb', 'feroxbuster', 'ffuf', 'theHarvester', 'wfuzz', 'arjun', 'paramspider', 'cmseek', 'curl']
        missing_tools = []
        
        print(f"{Colors.YELLOW}🔍 Checking dependencies...{Colors.END}")
        
        for tool in tools:
            try:
                subprocess.run(['which', tool], capture_output=True, check=True)
                print(f"{Colors.GREEN}✅ {tool} found{Colors.END}")
            except subprocess.CalledProcessError:
                print(f"{Colors.YELLOW}⚠️  {tool} not found{Colors.END}")
                missing_tools.append(tool)
        
        if missing_tools:
            print(f"\n{Colors.YELLOW}⚠️  Missing tools: {', '.join(missing_tools)}{Colors.END}")
            print(f"{Colors.CYAN}💡 Install missing tools to use all features{Colors.END}")
            return False
        else:
            print(f"{Colors.GREEN}✅ All dependencies found!{Colors.END}")
            return True 