import time
import os
import sys
from datetime import datetime

def monitor_status():
    """Monitor and display status updates from the main script"""
    status_file = 'status_log.txt'
    last_position = 0

    print("========================================")
    print("     SELENIUM DEPOSIT AUTOMATION STATUS")
    print("========================================")
    print()
    print("Monitoring status updates...")
    print()

    try:
        while True:
            if os.path.exists(status_file):
                try:
                    with open(status_file, 'r', encoding='utf-8') as f:
                        f.seek(last_position)
                        new_lines = f.readlines()
                        last_position = f.tell()

                        for line in new_lines:
                            line = line.strip()
                            if line:
                                print(line)
                                sys.stdout.flush()
                except Exception as e:
                    pass  # Continue monitoring even if there's a read error

            time.sleep(1)  # Check for updates every second

    except KeyboardInterrupt:
        print("\nStatus monitoring stopped.")
        sys.exit(0)
    except Exception as e:
        print(f"Status monitor error: {e}")
        time.sleep(5)  # Wait before retrying

if __name__ == "__main__":
    monitor_status()