#!/usr/bin/env python3
"""
Run the MCP Todo Server.

Usage:
    python -m src.mcp.run
    
Or directly:
    python src/mcp/run.py
"""

import asyncio
from src.mcp.server import main

if __name__ == "__main__":
    asyncio.run(main())
