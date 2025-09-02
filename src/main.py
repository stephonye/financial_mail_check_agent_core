#!/usr/bin/env python3
"""
AWS Bedrock AgentCore - Financial Email Processor
Main entry point for the application
"""
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from agents.customer_support import app

if __name__ == "__main__":
    print("Starting Financial Email Processor Agent...")
    app.run()
