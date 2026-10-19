#!/usr/bin/env python3
"""Research entry point for the shared runtime guard; install both skills together."""
from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).resolve().parents[2] / 'salestools-contact-management' /
                  'scripts' / 'validate_mcp_call.py'), run_name='__main__')
