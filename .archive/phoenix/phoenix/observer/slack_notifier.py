"""
Slack Notifications

Sends alerts to Slack when important things happen.
Completely optional - only configure if you want Slack alerts.

Note: Uses only standard library (urllib) - no external dependencies needed.
"""

import os
import json
import urllib.request
import urllib.error
import time
from typing import Optional, Dict, Any
from datetime import datetime

from phoenix.core.logging import get_logger

logger = get_logger(__name__)


class SlackNotifier:
    """
    Sends healing notifications to Slack.
    
    Optional module - doesn't affect healing if not configured.
    Just set SLACK_WEBHOOK_URL environment variable to enable.
    """
    
    def __init__(self, webhook_url: Optional[str] = None):
        """
        Initialize Slack notifier.
        
        Args:
            webhook_url: Slack webhook URL (or reads from env var)
        """
        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")
        self.logger = get_logger(__name__)
        self.enabled = bool(self.webhook_url)
        
        if self.enabled:
            self.logger.info("slack_notifier_enabled")
        else:
            self.logger.debug("slack_notifier_disabled")
    
    def notify_critical_failure(
        self,
        failure_type: str,
        agent_name: str,
        error_message: str,
    ):
        """
        Notify Slack of critical failure.
        
        Args:
            failure_type: Type of failure
            agent_name: Which agent failed
            error_message: Error details
        """
        if not self.enabled:
            return
        
        message = {
            "text": f"🚨 Critical Failure in Phoenix",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🚨 Critical Agentic AI Failure"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Failure Type:*\n{failure_type}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Agent:*\n{agent_name}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Error:*\n```{error_message[:200]}```"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"Phoenix is attempting autonomous fix • {datetime.utcnow().isoformat()}"
                        }
                    ]
                }
            ]
        }
        
        self._send_message(message)
    
    def notify_fix_success(
        self,
        failure_type: str,
        agent_name: str,
        fix_time_seconds: float,
    ):
        """
        Notify Slack of successful fix.
        
        Args:
            failure_type: Type of failure that was fixed
            agent_name: Which agent was fixed
            fix_time_seconds: How long the fix took
        """
        if not self.enabled:
            return
        
        message = {
            "text": f"✅ Autonomous Fix Applied",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "✅ Autonomous Fix Applied"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Failure:*\n{failure_type}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Agent:*\n{agent_name}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Fix Time:*\n{fix_time_seconds:.1f}s"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Status:*\nFixed automatically"
                        }
                    ]
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"No human intervention required • {datetime.utcnow().isoformat()}"
                        }
                    ]
                }
            ]
        }
        
        self._send_message(message)
    
    def notify_high_success_rate(self, success_rate: float):
        """Notify when success rate reaches milestone."""
        if not self.enabled or success_rate < 90:
            return
        
        emoji = "🏆" if success_rate > 95 else "⭐"
        
        message = {
            "text": f"{emoji} High Fix Success Rate",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"{emoji} *Phoenix Healing Success Rate: {success_rate:.1f}%*\n\nAutonomous fixes are working great!"
                    }
                }
            ]
        }
        
        self._send_message(message)
    
    def _send_message(self, message: Dict[str, Any]):
        """Send message to Slack using only standard library."""
        if not self.enabled:
            return
        
        max_retries = 3
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                # Prepare the request
                message_json = json.dumps(message)
                message_bytes = message_json.encode('utf-8')
                
                # Create request with proper headers
                webhook_url = self.webhook_url or ""
                if not webhook_url:
                    return
                req = urllib.request.Request(
                    webhook_url,
                    data=message_bytes,
                    headers={'Content-Type': 'application/json'},
                    method='POST',
                )
                
                # Send the request (blocks until done)
                with urllib.request.urlopen(req, timeout=5) as response:
                    status = response.status
                    
                    if status == 200:
                        self.logger.debug("slack_message_sent")
                        return
                    else:
                        self.logger.warning(
                            "slack_send_failed",
                            status=status,
                        )
                        return
            
            except urllib.error.URLError as e:
                # Network error - retry
                if attempt < max_retries - 1:
                    self.logger.debug(
                        "slack_retry",
                        attempt=attempt + 1,
                        error=str(e),
                    )
                    time.sleep(retry_delay)
                    retry_delay *= 2  # exponential backoff
                else:
                    self.logger.warning("slack_notification_failed", error=str(e))
                    return
            
            except Exception as e:
                # Any other error - log and stop
                self.logger.warning("slack_notification_error", error=str(e))
                return
