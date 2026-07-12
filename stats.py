"""Bomber statistics tracking with optional file persistence."""

import json
import os
import time
from dataclasses import dataclass, field
from typing import Dict, Optional

from base_service import SendResult, SendStatus


@dataclass
class ServiceStats:
    success: int = 0
    failed: int = 0
    rate_limited: int = 0
    timeout: int = 0
    blocked: int = 0
    last_sent: float = 0.0  # epoch timestamp

    @property
    def total(self) -> int:
        return self.success + self.failed + self.rate_limited + self.timeout + self.blocked

    def record(self, result: SendResult):
        if result.status == SendStatus.SUCCESS:
            self.success += 1
        elif result.status == SendStatus.FAILED:
            self.failed += 1
        elif result.status == SendStatus.RATE_LIMITED:
            self.rate_limited += 1
        elif result.status == SendStatus.TIMEOUT:
            self.timeout += 1
        elif result.status == SendStatus.BLOCKED:
            self.blocked += 1
        self.last_sent = time.time()


class BombStats:
    """Aggregate stats collector across all services."""

    def __init__(self):
        self.services: Dict[str, ServiceStats] = {}
        self.round: int = 0
        self.total_success: int = 0
        self.total_failed: int = 0
        self.total_errors: int = 0
        self.total_rate_limited: int = 0
        self.started_at: float = time.time()
        self.finished_at: float = 0.0

    def record(self, result: SendResult):
        name = result.service_name
        if name not in self.services:
            self.services[name] = ServiceStats()
        self.services[name].record(result)

        if result.is_success:
            self.total_success += 1
        elif result.is_error:
            self.total_errors += 1
        if result.status == SendStatus.FAILED:
            self.total_failed += 1
        elif result.status == SendStatus.RATE_LIMITED:
            self.total_rate_limited += 1

    def mark_finished(self):
        self.finished_at = time.time()

    @property
    def elapsed(self) -> float:
        end = self.finished_at or time.time()
        return end - self.started_at

    @property
    def total(self) -> int:
        return self.total_success + self.total_errors

    def summary(self) -> str:
        lines = [
            f"📊 Stats (round {self.round}, {self.elapsed:.1f}s)",
            f"  ✅ Success:       {self.total_success}",
            f"  ❌ Failed:        {self.total_failed}",
            f"  ⚠️  Errors:        {self.total_errors}",
            f"  🚫 Rate Limited:  {self.total_rate_limited}",
            f"  📨 Total:         {self.total}",
            "",
            "Per-service:",
        ]
        for name, svc in sorted(self.services.items()):
            lines.append(
                f"  {name:25s} ✅{svc.success:3d}  ❌{svc.failed:3d}  "
                f"🕐{svc.timeout:2d}  🚫{svc.rate_limited:2d}"
            )
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "round": self.round,
            "total_success": self.total_success,
            "total_failed": self.total_failed,
            "total_errors": self.total_errors,
            "total_rate_limited": self.total_rate_limited,
            "elapsed": self.elapsed,
            "services": {
                name: {
                    "success": svc.success,
                    "failed": svc.failed,
                    "rate_limited": svc.rate_limited,
                    "timeout": svc.timeout,
                    "blocked": svc.blocked,
                }
                for name, svc in self.services.items()
            },
        }

    def save(self, path: str):
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: str) -> Optional["BombStats"]:
        if not os.path.exists(path):
            return None
        with open(path) as f:
            data = json.load(f)
        stats = cls()
        stats.total_success = data.get("total_success", 0)
        stats.total_failed = data.get("total_failed", 0)
        stats.total_errors = data.get("total_errors", 0)
        stats.total_rate_limited = data.get("total_rate_limited", 0)
        stats.round = data.get("round", 0)
        for name, svc_data in data.get("services", {}).items():
            svc = ServiceStats(
                success=svc_data["success"],
                failed=svc_data["failed"],
                rate_limited=svc_data["rate_limited"],
                timeout=svc_data["timeout"],
                blocked=svc_data["blocked"],
            )
            stats.services[name] = svc
        return stats
