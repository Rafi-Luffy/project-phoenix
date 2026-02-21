#!/usr/bin/env python3
"""
Project Phoenix - Interactive Dashboard
Real-time monitoring dashboard for self-healing demo

This creates a live monitoring interface showing:
- System health metrics
- Event detection
- Active corrections
- Recovery progress
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, List
import sys
import os

BASE_URL = "http://localhost:8000/api/v1"

class Dashboard:
    """Live monitoring dashboard"""
    
    COLORS = {
        'HEADER': '\033[95m',
        'OKBLUE': '\033[94m',
        'OKCYAN': '\033[96m',
        'OKGREEN': '\033[92m',
        'WARNING': '\033[93m',
        'FAIL': '\033[91m',
        'ENDC': '\033[0m',
        'BOLD': '\033[1m',
        'UNDERLINE': '\033[4m',
        'GREY': '\033[90m',
    }
    
    def __init__(self):
        self.systems: Dict[str, Any] = {}
        self.events: List[Dict[str, Any]] = []
        self.corrections: List[Dict[str, Any]] = []
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def color(self, text: str, color: str) -> str:
        """Apply color to text"""
        return f"{self.COLORS[color]}{text}{self.COLORS['ENDC']}"
    
    def bold(self, text: str) -> str:
        """Make text bold"""
        return f"{self.COLORS['BOLD']}{text}{self.COLORS['ENDC']}"
    
    def health_bar(self, value: float, width: int = 30) -> str:
        """Create a health bar visualization"""
        filled = int(width * value / 100) if value > 0 else 0
        empty = width - filled
        
        if value >= 80:
            color = 'OKGREEN'
        elif value >= 50:
            color = 'WARNING'
        else:
            color = 'FAIL'
        
        bar = f"[{self.color('█' * filled, color)}{'░' * empty}] {value:.1f}%"
        return bar
    
    def status_badge(self, status: str) -> str:
        """Create a status badge"""
        status_upper = status.upper()
        
        if status_upper == "HEALTHY":
            return self.color(f"● {status_upper}", 'OKGREEN')
        elif status_upper == "WARNING":
            return self.color(f"● {status_upper}", 'WARNING')
        elif status_upper == "CRITICAL" or status_upper == "ERROR":
            return self.color(f"● {status_upper}", 'FAIL')
        else:
            return self.color(f"● {status_upper}", 'OKCYAN')
    
    def fetch_systems(self):
        """Fetch systems from API"""
        try:
            response = requests.get(f"{BASE_URL}/systems")
            if response.status_code == 200:
                systems = response.json()
                for system in systems:
                    self.systems[system['id']] = system
            return True
        except:
            return False
    
    def fetch_events(self, limit: int = 10):
        """Fetch recent events"""
        try:
            response = requests.get(
                f"{BASE_URL}/events",
                params={"limit": limit}
            )
            if response.status_code == 200:
                self.events = response.json()
            return True
        except:
            return False
    
    def fetch_corrections(self, limit: int = 10):
        """Fetch recent corrections"""
        try:
            response = requests.get(
                f"{BASE_URL}/corrections",
                params={"limit": limit}
            )
            if response.status_code == 200:
                self.corrections = response.json()
            return True
        except:
            return False
    
    def render_header(self):
        """Render dashboard header"""
        title = "PROJECT PHOENIX - LIVE MONITORING DASHBOARD"
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        print(self.color("╔" + "═" * 118 + "╗", 'HEADER'))
        print(self.color(f"║ {title.center(116)} ║", 'HEADER'))
        print(self.color(f"║ {timestamp.center(116)} ║", 'HEADER'))
        print(self.color("╚" + "═" * 118 + "╝", 'HEADER'))
        print()
    
    def render_systems_panel(self):
        """Render systems monitoring panel"""
        print(self.bold("REGISTERED SYSTEMS"))
        print(self.color("─" * 120, 'GREY'))
        
        if not self.systems:
            print(self.color("  No systems registered", 'GREY'))
            print()
            return
        
        for system_id, system in list(self.systems.items())[:5]:  # Show max 5
            # Fetch detailed status
            try:
                response = requests.get(f"{BASE_URL}/systems/{system_id}/status")
                if response.status_code == 200:
                    status = response.json()
                    
                    print(f"\n  {self.bold(system['name'])} [{self.color(system_id[:8], 'GREY')}...]")
                    print(f"    Type: {system['type']} | Status: {self.status_badge(system.get('status', 'unknown'))}")
                    print(f"    Health: {self.health_bar(status.get('health_score', 0) * 100)}")
                    print(f"    Uptime: {status.get('uptime_percentage', 0)}% | Error Rate: {status.get('error_rate', 0)}%")
                    print(f"    Active Events: {status.get('active_events', 0)} | Active Corrections: {status.get('active_corrections', 0)}")
            except:
                print(f"\n  {self.bold(system['name'])}")
                print(f"    Unable to fetch detailed status")
        
        print()
    
    def render_events_panel(self):
        """Render recent events panel"""
        print(self.bold("RECENT EVENTS"))
        print(self.color("─" * 120, 'GREY'))
        
        if not self.events:
            print(self.color("  No events detected", 'GREY'))
            print()
            return
        
        for event in self.events[:5]:  # Show max 5
            severity_color = {
                'info': 'OKCYAN',
                'warning': 'WARNING',
                'critical': 'FAIL',
                'error': 'FAIL'
            }.get(event.get('severity', 'info'), 'OKCYAN')
            
            severity_badge = self.color(f"[{event.get('severity', 'N/A').upper()}]", severity_color)
            
            # Parse timestamp
            try:
                event_time = datetime.fromisoformat(event.get('detected_at', '').replace('Z', '+00:00'))
                time_ago = (datetime.utcnow() - event_time.replace(tzinfo=None)).seconds
                time_str = f"{time_ago}s ago" if time_ago < 60 else f"{time_ago//60}m ago"
            except:
                time_str = "recently"
            
            print(f"  {severity_badge} {self.bold(event.get('title', 'Unknown'))} ({self.color(time_str, 'GREY')})")
            print(f"       {event.get('description', 'No description')}")
        
        print()
    
    def render_corrections_panel(self):
        """Render recent corrections panel"""
        print(self.bold("APPLIED CORRECTIONS"))
        print(self.color("─" * 120, 'GREY'))
        
        if not self.corrections:
            print(self.color("  No corrections applied yet", 'GREY'))
            print()
            return
        
        for correction in self.corrections[:5]:  # Show max 5
            status_color = {
                'successful': 'OKGREEN',
                'pending': 'WARNING',
                'failed': 'FAIL'
            }.get(correction.get('status', 'unknown'), 'OKCYAN')
            
            status_badge = self.color(f"[{correction.get('status', 'N/A').upper()}]", status_color)
            
            action = self.bold(correction.get('action_type', 'unknown').upper())
            target = self.color(correction.get('target', 'unknown'), 'GREY')
            duration = f"{correction.get('duration_ms', 0)}ms" if correction.get('duration_ms') else "pending"
            
            print(f"  {status_badge} {action} on {target} ({self.color(duration, 'GREY')})")
        
        print()
    
    def render_stats_panel(self):
        """Render statistics panel"""
        print(self.bold("STATISTICS"))
        print(self.color("─" * 120, 'GREY'))
        
        try:
            # Systems count
            systems_count = len(self.systems)
            events_count = len(self.events)
            corrections_count = len(self.corrections)
            
            print(f"  {self.color('●', 'OKCYAN')} Registered Systems: {self.bold(str(systems_count))}")
            print(f"  {self.color('●', 'FAIL')} Events Detected: {self.bold(str(events_count))}")
            print(f"  {self.color('●', 'OKGREEN')} Corrections Applied: {self.bold(str(corrections_count))}")
            
            # Success rate
            if corrections_count > 0:
                successful = sum(1 for c in self.corrections if c.get('status') == 'successful')
                success_rate = (successful / corrections_count) * 100
                print(f"  {self.color('●', 'OKGREEN')} Success Rate: {self.bold(f'{success_rate:.1f}%')}")
            
            print()
        except:
            print(self.color("  Unable to calculate statistics", 'GREY'))
            print()
    
    def render_footer(self):
        """Render dashboard footer"""
        print(self.color("╔" + "═" * 118 + "╗", 'HEADER'))
        help_text = "Press Ctrl+C to exit | Refresh rate: 2 seconds | Backend: http://localhost:8000"
        print(self.color(f"║ {help_text.center(116)} ║", 'HEADER'))
        print(self.color("╚" + "═" * 118 + "╝", 'HEADER'))
    
    def refresh(self):
        """Refresh all data and render dashboard"""
        self.clear_screen()
        
        # Fetch data
        self.fetch_systems()
        self.fetch_events()
        self.fetch_corrections()
        
        # Render
        self.render_header()
        self.render_systems_panel()
        self.render_events_panel()
        self.render_corrections_panel()
        self.render_stats_panel()
        self.render_footer()
    
    def run(self):
        """Run the live dashboard"""
        try:
            while True:
                self.refresh()
                time.sleep(2)  # Refresh every 2 seconds
        except KeyboardInterrupt:
            self.clear_screen()
            print("\n" + self.color("Dashboard closed", 'OKCYAN'))
            sys.exit(0)

if __name__ == "__main__":
    dashboard = Dashboard()
    dashboard.run()
