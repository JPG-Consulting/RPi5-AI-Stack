from __future__ import annotations
import threading
from collections import defaultdict

class Metrics:
    def __init__(self):
        self.lock = threading.Lock()
        self.counters = defaultdict(int)
        self.timers = defaultdict(list)

    def inc(self, name: str, value: int = 1):
        with self.lock:
            self.counters[name] += value

    def observe_ms(self, name: str, ms: float):
        with self.lock:
            self.timers[name].append(ms)

    def snapshot(self) -> dict:
        with self.lock:
            return {
                "counters": dict(self.counters),
                "timers": {
                    k: {
                        "count": len(v),
                        "min_ms": min(v) if v else None,
                        "max_ms": max(v) if v else None,
                        "avg_ms": (sum(v) / len(v)) if v else None,
                    }
                    for k, v in self.timers.items()
                },
            }

metrics = Metrics()
