#!/usr/bin/env python3
"""
Rich-powered progress indicators for ipsnipe
Simplified progress display with better visuals
"""

import time
import threading
import os
import sys
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.live import Live
from rich.text import Text

console = Console()

def check_for_keypress():
    """Check if a key has been pressed (non-blocking)"""
    try:
        if os.name == 'posix':
            import select
            import tty
            import termios
            
            old_settings = termios.tcgetattr(sys.stdin)
            try:
                tty.setraw(sys.stdin.fileno())
                if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
                    char = sys.stdin.read(1).lower()
                    return char
            finally:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    except Exception:
        pass
    return None


class SimpleProgressIndicator:
    """Rich-powered progress indicator with keyboard controls"""
    
    def __init__(self, description: str, timeout: int):
        self.description = description
        self.timeout = timeout
        self.start_time = None
        self.is_running = False
        self.thread = None
        self.skipped = False
        self.quit_requested = False
        
    def start(self):
        """Start the progress indicator"""
        self.start_time = time.time()
        self.is_running = True
        
        # Show start message with Rich
        console.print(f"⏳ {self.description}...", style="cyan")
        
        # Start monitoring thread
        self.thread = threading.Thread(target=self._monitor, daemon=True)
        self.thread.start()
    
    def stop(self, status: str = "completed", execution_time: float = None):
        """Stop and show final status"""
        self.is_running = False
        
        if self.thread:
            self.thread.join(timeout=0.5)
        
        elapsed = execution_time or (time.time() - self.start_time if self.start_time else 0)
        
        # Show final status with Rich
        if self.skipped:
            console.print(f"⏭️  {self.description} - Skipped", style="yellow")
            return "skipped"
        elif self.quit_requested:
            console.print(f"❌ {self.description} - Quit requested", style="red")
            return "quit"
        elif status == "completed":
            console.print(f"✅ {self.description} - Done ({elapsed:.0f}s)", style="green")
        elif status == "failed":
            console.print(f"❌ {self.description} - Failed", style="red")
        elif status == "timeout":
            console.print(f"⏰ {self.description} - Timeout", style="yellow")
        else:
            console.print(f"ℹ️  {self.description} - {status}", style="cyan")
        
        return status
    
    def _monitor(self):
        """Monitor for user input"""
        while self.is_running:
            try:
                if os.name == 'posix':
                    key = check_for_keypress()
                    if key == 's':
                        self.skipped = True
                        self.is_running = False
                        break
                    elif key == 'q':
                        self.quit_requested = True
                        self.is_running = False
                        break
                
                time.sleep(0.5)
            except Exception:
                break


class ProgressBar:
    """Rich-powered progress bar with controls"""
    
    def __init__(self, description: str, total_time: int = None):
        self.description = description
        self.total_time = total_time
        self.start_time = None
        self.is_running = False
        self.thread = None
        self.skipped = False
        self.quit_requested = False
        
    def start(self):
        """Start the progress indicator"""
        self.start_time = time.time()
        self.is_running = True
        
        # Simple start message with controls
        console.print(f"⏳ {self.description} - Press 's' to skip, 'q' to quit", style="cyan")
        
        self.thread = threading.Thread(target=self._monitor, daemon=True)
        self.thread.start()
    
    def stop(self, status: str = "completed"):
        """Stop and show final status"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=1)
        
        elapsed = time.time() - self.start_time if self.start_time else 0
        
        if self.skipped:
            console.print(f"⏭️  {self.description} - Skipped", style="yellow")
        elif self.quit_requested:
            console.print(f"❌ {self.description} - Quit requested", style="red")
        elif status == "completed":
            console.print(f"✅ {self.description} - Completed ({elapsed:.0f}s)", style="green")
        elif status == "failed":
            console.print(f"❌ {self.description} - Failed", style="red")
        elif status == "timeout":
            console.print(f"⏰ {self.description} - Timeout", style="yellow")
        else:
            console.print(f"ℹ️  {self.description} - {status}", style="cyan")
    
    def _monitor(self):
        """Monitor for user input"""
        while self.is_running:
            if os.name == 'posix':
                key = check_for_keypress()
                if key == 's':
                    self.skipped = True
                    self.is_running = False
                    break
                elif key == 'q':
                    self.quit_requested = True
                    self.is_running = False
                    break
            
            time.sleep(0.5)


class ScanProgressIndicator:
    """Rich-powered scan progress with beautiful spinner"""
    
    def __init__(self, description: str, timeout: int):
        self.description = description
        self.timeout = timeout
        self.start_time = None
        self.is_running = False
        self.skipped = False
        self.quit_requested = False
        self.progress = None
        self.task_id = None
        self.thread = None
        
    def start(self):
        """Start progress indication with Rich spinner"""
        self.start_time = time.time()
        self.is_running = True
        
        # Create Rich progress display
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=console,
            transient=True  # Remove when done
        )
        
        self.progress.start()
        self.task_id = self.progress.add_task(
            f"{self.description} (Press 's' to skip, 'q' to quit)", 
            total=None
        )
        
        # Start input monitoring
        self.thread = threading.Thread(target=self._monitor_input, daemon=True)
        self.thread.start()
    
    def stop(self, status: str = "completed", execution_time: float = None):
        """Stop progress and show final status"""
        self.is_running = False
        
        if self.progress:
            self.progress.stop()
        
        if self.thread:
            self.thread.join(timeout=1)
        
        elapsed = execution_time or (time.time() - self.start_time if self.start_time else 0)
        
        # Show final status
        if self.skipped:
            console.print(f"⏭️  {self.description} - Skipped", style="yellow")
            return "skipped"
        elif self.quit_requested:
            console.print(f"❌ {self.description} - Quit requested", style="red")
            return "quit"
        elif status == "completed":
            console.print(f"✅ {self.description} - Done ({elapsed:.0f}s)", style="green")
        elif status == "failed":
            console.print(f"❌ {self.description} - Failed", style="red")
        elif status == "timeout":
            console.print(f"⏰ {self.description} - Timeout", style="yellow")
        else:
            console.print(f"ℹ️  {self.description} - {status}", style="cyan")
        
        return status
    
    def _monitor_input(self):
        """Monitor for user input"""
        while self.is_running:
            if os.name == 'posix':
                key = check_for_keypress()
                if key == 's':
                    self.skipped = True
                    self.is_running = False
                    break
                elif key == 'q':
                    self.quit_requested = True
                    self.is_running = False
                    break
            
            time.sleep(0.5)


def show_loading_dots(message: str, duration: float = 2.0):
    """Show a simple loading message with Rich"""
    with console.status(f"[cyan]{message}..."):
        time.sleep(duration)


def clear_line():
    """Clear current line (not needed with Rich but kept for compatibility)"""
    pass 