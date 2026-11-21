#!/usr/bin/env python3
"""Next-steps entry point for the deal review runtime guard; install all skills together."""
from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).resolve().parents[2] / 'sales-deal-review' /
                  'scripts' / 'validate_mcp_call.py'), run_name='__main__')
