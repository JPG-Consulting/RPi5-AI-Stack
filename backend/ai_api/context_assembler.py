from __future__ import annotations
from typing import List, Dict

def assemble(messages: List[Dict], last_n_turns: int) -> List[Dict]:
    # Keep system messages (if persisted) plus last N user/assistant turns.
    ua = [m for m in messages if m.get("role") in ("user", "assistant")]
    tail = ua[-(last_n_turns * 2):]
    sys_msgs = [m for m in messages if m.get("role") == "system"]
    return sys_msgs + tail
