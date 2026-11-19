# -*- coding: utf-8 -*-
import json
from pathlib import Path

# Load binders
with open(r"C:\Users\TP.KHOAXETNGHIEM\.gemini\antigravity\scratch\khoa_xet_nghiem_app\binders_def.json", "r", encoding="utf-8") as f:
    binders = json.load(f)

print("Loaded binders:", len(binders))
