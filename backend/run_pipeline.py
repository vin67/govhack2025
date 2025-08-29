#!/usr/bin/env python3
"""
GovHack 2025 Multi-Agent Anti-Scam Pipeline
Main entry point for running the complete pipeline
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.agent_framework import run_pipeline

def main():
    """Main entry point for the multi-agent pipeline"""
    print("🛡️ GovHack 2025: Multi-Agent Anti-Scam Data Pipeline")
    print("=" * 60)
    print("Starting complete pipeline execution...")
    
    # Run the multi-agent framework
    run_pipeline()

if __name__ == "__main__":
    main()