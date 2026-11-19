import os
import sys
from pathlib import Path

# Set up project path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
os.environ["PYTHONPATH"] = str(ROOT_DIR)

from backend.main import app

# Vercel Serverless Function entry point
app = app
