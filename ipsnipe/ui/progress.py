#!/usr/bin/env python3
"""
Timer-based progress indicators and loading effects for ipsnipe
"""

import sys
import time
import threading
from .colors import Colors


class ProgressBar:
    """Dynamic timer display that updates in place without creating new lines"""
    
    def __init__(self, description: str, total_time: int = None):
        self.description = description
        self.total_time = total_time
        self.start_time = None
        self.is_running = False
        self.thread = None
        
    def start(self):
        """Start the timer animation"""
        self.start_time = time.time()
        self.is_running = True
        self.thread = threading.Thread(target=self._animate, daemon=True)
        self.thread.start()
    
    def stop(self, status: str = "completed"):
        """Stop the timer and show final status"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=1)
        
        elapsed = time.time() - self.start_time if self.start_time else 0
        
        # Clear the line and show final status
        sys.stdout.write('\r\033[K')  # Clear line
        sys.stdout.flush()
        
        if status == "completed":
            print(f"{Colors.GREEN}✅ {self.description} - Completed ({elapsed:.1f}s){Colors.END}")
        elif status == "skipped":
            print(f"{Colors.YELLOW}⏭️  {self.description} - Skipped{Colors.END}")
        elif status == "failed":
            print(f"{Colors.RED}❌ {self.description} - Failed ({elapsed:.1f}s){Colors.END}")
        elif status == "timeout":
            print(f"{Colors.YELLOW}⏰ {self.description} - Timed out ({elapsed:.1f}s){Colors.END}")
        else:
            print(f"{Colors.CYAN}🔄 {self.description} - {status} ({elapsed:.1f}s){Colors.END}")
    
    def _animate(self):
        """Animate the progress timer without visual bar"""
        animation_chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        char_index = 0
        
        while self.is_running:
            elapsed = time.time() - self.start_time
            
            if self.total_time:
                # Show progress with percentage and time remaining
                progress = min(elapsed / self.total_time, 1.0)
                percentage = int(progress * 100)
                remaining = max(0, self.total_time - elapsed)
                
                # Format times
                elapsed_mins, elapsed_secs = divmod(int(elapsed), 60)
                elapsed_str = f"{elapsed_mins:02d}:{elapsed_secs:02d}"
                
                if remaining > 0:
                    remaining_mins, remaining_secs = divmod(int(remaining), 60)
                    remaining_str = f"{remaining_mins:02d}:{remaining_secs:02d}"
                    time_display = f"⏱️  {elapsed_str} elapsed, {remaining_str} remaining ({percentage}%)"
                else:
                    time_display = f"⏱️  {elapsed_str} elapsed (100%+)"
                
                status_line = (f"\r{Colors.CYAN}{animation_chars[char_index]} "
                             f"{self.description} - {time_display}{Colors.END}")
            else:
                # Show elapsed time only
                mins, secs = divmod(int(elapsed), 60)
                time_str = f"{mins:02d}:{secs:02d}" if mins > 0 else f"{secs:02d}s"
                
                status_line = (f"\r{Colors.CYAN}{animation_chars[char_index]} "
                             f"{self.description} - ⏱️  {time_str} elapsed{Colors.END}")
            
            sys.stdout.write(f"\r\033[K{status_line}")
            sys.stdout.flush()
            
            char_index = (char_index + 1) % len(animation_chars)
            time.sleep(0.1)


class ScanProgressIndicator:
    """Specialized timer indicator for scans with timeout tracking"""
    
    def __init__(self, description: str, timeout: int):
        self.description = description
        self.timeout = timeout
        self.start_time = None
        self.is_running = False
        self.thread = None
        
    def start(self):
        """Start the scan timer indicator"""
        self.start_time = time.time()
        self.is_running = True
        self.thread = threading.Thread(target=self._show_progress, daemon=True)
        self.thread.start()
    
    def stop(self, status: str = "completed", execution_time: float = None):
        """Stop the timer indicator and clear the line for next output"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=0.5)
        
        # Clear the progress line completely
        sys.stdout.write('\r\033[K')
        sys.stdout.flush()
        
        # Don't print anything here - let the calling function handle status output
    
    def _show_progress(self):
        """Show the progress timer without visual bar"""
        spinner_chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        spinner_index = 0
        
        while self.is_running:
            try:
                elapsed = time.time() - self.start_time
                remaining = max(0, self.timeout - elapsed)
                
                # Calculate progress percentage for color coding
                progress = min(elapsed / self.timeout, 1.0)
                
                # Format elapsed time
                elapsed_mins, elapsed_secs = divmod(int(elapsed), 60)
                elapsed_str = f"{elapsed_mins:02d}:{elapsed_secs:02d}"
                
                # Format remaining time
                if remaining > 0:
                    remaining_mins, remaining_secs = divmod(int(remaining), 60)
                    remaining_str = f"{remaining_mins:02d}:{remaining_secs:02d}"
                    time_display = f"⏱️  {elapsed_str} elapsed, {remaining_str} remaining"
                else:
                    time_display = f"⏱️  {elapsed_str} elapsed (overtime)"
                
                # Show different colors based on progress
                if progress < 0.7:
                    color = Colors.GREEN
                elif progress < 0.9:
                    color = Colors.YELLOW
                else:
                    color = Colors.RED
                
                # Build the progress line - compact timer format
                short_desc = self.description[:40] + "..." if len(self.description) > 40 else self.description
                progress_line = (f"{color}{spinner_chars[spinner_index]} "
                               f"{short_desc} - {time_display}{Colors.END}")
                
                # Clear line completely and write progress
                sys.stdout.write(f"\r\033[K{progress_line}")
                sys.stdout.flush()
                
                spinner_index = (spinner_index + 1) % len(spinner_chars)
                time.sleep(0.2)
                
            except Exception:
                # If anything goes wrong, just break out quietly
                break


def show_loading_dots(message: str, duration: float = 3.0):
    """Show a simple loading animation with dots"""
    print(f"{Colors.CYAN}{message}", end="", flush=True)
    
    start_time = time.time()
    dot_count = 0
    
    while time.time() - start_time < duration:
        if dot_count < 3:
            print(".", end="", flush=True)
            dot_count += 1
        else:
            # Clear dots and restart
            print("\b\b\b   \b\b\b", end="", flush=True)
            dot_count = 0
        
        time.sleep(0.5)
    
    print(f" Done!{Colors.END}")


def clear_line():
    """Clear the current line in terminal"""
    sys.stdout.write('\r\033[K')
    sys.stdout.flush() 