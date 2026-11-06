#!/usr/bin/env python3
"""
notify_dispatcher.py
Automated Webhook & Incident Dispatcher for Antigravity Agent Hub.

Dispatches real-time alerts, incident reports, and system notifications to:
- Telegram (via Bot API)
- Discord (via Incoming Webhook Embeds)
- Slack (via Incoming Webhook Blocks)
- Generic HTTP Webhook (POST JSON)
- Local File Logger (logs/incident_dispatch.log)

Zero external dependencies: uses Python standard library (urllib.request, json).
Graceful fallbacks: Never interrupts running automated pipelines if network fails.
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

# Ensure UTF-8 standard IO for Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

SEVERITY_COLORS = {
    "INFO": 0x3498DB,      # Blue
    "SUCCESS": 0x2ECC71,   # Green
    "WARNING": 0xF39C12,   # Amber
    "ERROR": 0xE74C3C,     # Red
    "CRITICAL": 0x9B59B6   # Purple/Dark Red
}

SEVERITY_EMOJIS = {
    "INFO": "ℹ️",
    "SUCCESS": "✅",
    "WARNING": "⚠️",
    "ERROR": "🚨",
    "CRITICAL": "🔥"
}


def load_env_file(env_path: Path):
    """Loads key=value pairs into os.environ if not already set."""
    if not env_path.exists():
        return
    try:
        with open(env_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                k, v = line.split('=', 1)
                k = k.strip()
                v = v.strip().strip("'\"")
                if k and k not in os.environ:
                    os.environ[k] = v
    except Exception:
        pass


def post_json(url: str, payload: Dict[str, Any], timeout: int = 5) -> Tuple[bool, str]:
    """Sends JSON POST request using standard urllib."""
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Antigravity-NotifyDispatcher/1.0"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            status_code = response.getcode()
            body = response.read().decode('utf-8', errors='ignore')
            return True, f"HTTP {status_code}: {body[:100]}"
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8', errors='ignore') if hasattr(e, 'read') else ''
        return False, f"HTTP Error {e.code}: {err_body[:100]}"
    except Exception as e:
        return False, f"Network Error: {str(e)}"


class IncidentDispatcher:
    def __init__(self, root_dir: Optional[Path] = None):
        self.root_dir = root_dir or Path.cwd()
        # Auto-load .env from root or parent
        for candidate in [self.root_dir / ".env", self.root_dir.parent / ".env"]:
            load_env_file(candidate)

        self.telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = os.environ.get("TELEGRAM_CHAT_ID")
        self.discord_url = os.environ.get("DISCORD_WEBHOOK_URL")
        self.slack_url = os.environ.get("SLACK_WEBHOOK_URL")
        self.generic_url = os.environ.get("GENERIC_WEBHOOK_URL")

        self.log_file = self.root_dir / "logs" / "incident_dispatch.log"

    def log_locally(self, event: Dict[str, Any]):
        """Appends the incident event to logs/incident_dispatch.log."""
        try:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(event, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"Warning: Failed to write to local incident log: {e}", file=sys.stderr)

    def dispatch(
        self,
        event_type: str,
        title: str,
        message: str,
        severity: str = "INFO",
        project: str = "Agent-Hub",
        metadata: Optional[Dict[str, Any]] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        severity = severity.upper()
        if severity not in SEVERITY_COLORS:
            severity = "INFO"

        now_iso = datetime.now(timezone.utc).isoformat()
        emoji = SEVERITY_EMOJIS.get(severity, "ℹ️")

        event_payload = {
            "timestamp": now_iso,
            "project": project,
            "event_type": event_type,
            "severity": severity,
            "title": title,
            "message": message,
            "metadata": metadata or {}
        }

        # Always log locally
        self.log_locally(event_payload)

        results = {
            "event": event_payload,
            "dispatched": {},
            "dry_run": dry_run
        }

        # 1. Telegram Dispatch
        if self.telegram_token and self.telegram_chat_id:
            tg_text = (
                f"{emoji} *[{severity}] {title}*\n"
                f"📁 *Project:* `{project}`\n"
                f"🏷️ *Type:* `{event_type}`\n\n"
                f"{message}"
            )
            if dry_run:
                results["dispatched"]["telegram"] = {"status": "DRY_RUN", "preview": tg_text}
            else:
                tg_url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
                tg_payload = {
                    "chat_id": self.telegram_chat_id,
                    "text": tg_text,
                    "parse_mode": "Markdown"
                }
                ok, resp = post_json(tg_url, tg_payload)
                results["dispatched"]["telegram"] = {"status": "SUCCESS" if ok else "FAILED", "details": resp}

        # 2. Discord Dispatch
        if self.discord_url:
            dc_color = SEVERITY_COLORS.get(severity, 0x3498DB)
            dc_payload = {
                "embeds": [{
                    "title": f"{emoji} [{severity}] {title}",
                    "description": message,
                    "color": dc_color,
                    "fields": [
                        {"name": "Project", "value": project, "inline": True},
                        {"name": "Event Type", "value": event_type, "inline": True},
                        {"name": "Timestamp", "value": now_iso, "inline": False}
                    ],
                    "footer": {"text": "Antigravity Hub Incident Dispatcher"}
                }]
            }
            if dry_run:
                results["dispatched"]["discord"] = {"status": "DRY_RUN", "payload": dc_payload}
            else:
                ok, resp = post_json(self.discord_url, dc_payload)
                results["dispatched"]["discord"] = {"status": "SUCCESS" if ok else "FAILED", "details": resp}

        # 3. Slack Dispatch
        if self.slack_url:
            slack_payload = {
                "text": f"{emoji} *[{severity}] {title}*",
                "blocks": [
                    {
                        "type": "header",
                        "text": {"type": "plain_text", "text": f"{emoji} [{severity}] {title}", "emoji": True}
                    },
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": message}
                    },
                    {
                        "type": "context",
                        "elements": [
                            {"type": "mrkdwn", "text": f"*Project:* {project} | *Type:* {event_type} | *Time:* {now_iso}"}
                        ]
                    }
                ]
            }
            if dry_run:
                results["dispatched"]["slack"] = {"status": "DRY_RUN", "payload": slack_payload}
            else:
                ok, resp = post_json(self.slack_url, slack_payload)
                results["dispatched"]["slack"] = {"status": "SUCCESS" if ok else "FAILED", "details": resp}

        # 4. Generic Webhook Dispatch
        if self.generic_url:
            if dry_run:
                results["dispatched"]["generic"] = {"status": "DRY_RUN", "payload": event_payload}
            else:
                ok, resp = post_json(self.generic_url, event_payload)
                results["dispatched"]["generic"] = {"status": "SUCCESS" if ok else "FAILED", "details": resp}

        if not results["dispatched"]:
            results["dispatched"]["local_log_only"] = {
                "status": "RECORDED",
                "file": str(self.log_file),
                "notice": "No webhook environment variables configured (DISCORD_WEBHOOK_URL, TELEGRAM_BOT_TOKEN, SLACK_WEBHOOK_URL)."
            }

        return results


def main():
    parser = argparse.ArgumentParser(
        description="Automated Webhook & Incident Dispatcher for Antigravity Hub",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--type", "-t", default="SYSTEM_ALERT", help="Event type (QA_ESCALATE, SECRET_LEAK, TOKEN_OVERFLOW, DEPLOY_SUCCESS, etc.)")
    parser.add_argument("--title", required=False, default="System Event", help="Short summary / title of the incident")
    parser.add_argument("--message", "-m", required=False, default="An automated event was triggered.", help="Detailed incident message")
    parser.add_argument("--severity", "-s", choices=["INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"], default="INFO", help="Incident severity level")
    parser.add_argument("--project", "-p", default="Agent-Hub", help="Project identifier (e.g. dental_project, vietjet-airflow)")
    parser.add_argument("--json", action="store_true", help="Emit Zero-Fat M2M JSON output")
    parser.add_argument("--dry-run", action="store_true", help="Format and test payloads without sending network requests")
    parser.add_argument("--test", action="store_true", help="Send a test verification notification across all channels")

    args = parser.parse_args()

    dispatcher = IncidentDispatcher()

    if args.test:
        title = "Antigravity Notification Health Check"
        message = "Test ping dispatched from Antigravity Agent Hub CLI."
        severity = "SUCCESS"
        event_type = "HEALTHCHECK"
    else:
        title = args.title
        message = args.message
        severity = args.severity
        event_type = args.type

    result = dispatcher.dispatch(
        event_type=event_type,
        title=title,
        message=message,
        severity=severity,
        project=args.project,
        dry_run=args.dry_run
    )

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        emoji = SEVERITY_EMOJIS.get(severity, "ℹ️")
        print("\n" + "=" * 65)
        print(f" {emoji}  INCIDENT DISPATCHER: [{severity}] {title}")
        print("=" * 65)
        print(f" Project : {args.project}")
        print(f" Type    : {event_type}")
        print(f" Message : {message}")
        print("-" * 65)
        print(" Dispatch Channels:")
        for ch, info in result["dispatched"].items():
            status = info.get("status", "UNKNOWN")
            print(f"   • {ch:<14}: [{status}] {info.get('details', info.get('notice', ''))}")
        print("=" * 65 + "\n")


if __name__ == "__main__":
    main()
