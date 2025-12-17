from __future__ import annotations
import re

_REPEAT = re.compile(r"^\s*(repite|repiteme|repíteme|podr(i|í)as repetir)\s*[\.\?!]*\s*$", re.I)
_META = re.compile(r"^\s*(de qu(e|é) est(á|a)bamos hablando|me puedes decir de qu(e|é) hablamos la (u|ú)ltima vez|de qu(e|é) estamos hablando)\s*[\.\?!]*\s*$", re.I)

class Decision:
    def __init__(self, kind: str):
        self.kind = kind  # 'repeat_last' | 'meta_summary' | 'normal'

def decide(user_text: str) -> Decision:
    if _REPEAT.match(user_text or ""):
        return Decision("repeat_last")
    if _META.match(user_text or ""):
        return Decision("meta_summary")
    return Decision("normal")
