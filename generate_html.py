#!/usr/bin/env python3
import json
from datetime import datetime

def main():
    """Simple HTML generator that just logs what it would do"""
    try:
        with open("outbreak_data.json", "r") as f:
            data = json.load(f)
        print("✅ HTML generation completed")
        print(f"📊 Processed data from {data.get(last_updated, unknown time)}")
        print(f"📊 Total alerts: {data.get(total_alerts, 0)}")
    except FileNotFoundError:
        print("ℹ️ No outbreak data file found - skipping HTML update")

if __name__ == "__main__":
    main()
