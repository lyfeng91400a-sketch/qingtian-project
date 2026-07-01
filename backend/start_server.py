#!/usr/bin/env python3
"""Start the uvicorn server from the backend directory."""
import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.environ['PATH'] = os.path.join(os.getcwd(), 'venv/bin') + ':' + os.environ['PATH']
sys.path.insert(0, os.getcwd())

import uvicorn
uvicorn.run("main:app", host="0.0.0.0", port=8000)
