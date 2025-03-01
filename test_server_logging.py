"""
Test script for the server-side logging API
This script tests sending client logs to the server and retrieving them
"""

import requests
import json
import time
import random
import argparse
import os
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
AUTH_URL = f"{BASE_URL}/auth/token/"
LOGS_URL = f"{BASE_URL}/logs/client/"

# Test user credentials (update these with valid credentials)
TEST_USER = {
    "username": "admin",
    "password": "admin"  # Change this to a valid password
}

def generate_test_logs(count=50):
    """Generate sample logs for testing"""
    log_levels = ["DEBUG", "INFO", "WARN", "ERROR", "LOG"]
    log_messages = [
        "User logged in",
        "Data loaded successfully",
        "Form validation failed",
        "API request completed",
        "Navigation event",
        "Button clicked",
        "Form submitted",
        "Error occurred during processing",
        "Database query executed",
        "Permission check failed",
        "Connection timeout"
    ]
    
    logs = []
    now = datetime.now().isoformat()
    
    for i in range(count):
        level = random.choice(log_levels)
        message = random.choice(log_messages) + f" (#{i})"
        
        # Add some structured data occasionally
        data = None
        if random.random() > 0.5:
            data = {
                "requestId": f"req-{random.randint(1000, 9999)}",
                "userId": random.randint(1, 100),
                "duration": round(random.random() * 1000, 2),
                "status": random.choice(["success", "failure", "pending"])
            }
        
        logs.append({
            "timestamp": now,
            "level": level,
            "message": message,
            "data": json.dumps(data) if data else None
        })
    
    return logs

def get_auth_token():
    """Get JWT authentication token"""
    try:
        response = requests.post(AUTH_URL, json=TEST_USER)
        if response.status_code == 200:
            return response.json()["access"]
        else:
            print(f"Auth failed: {response.status_code} {response.text}")
            return None
    except Exception as e:
        print(f"Error getting auth token: {str(e)}")
        return None

def send_logs_to_server(logs, token=None):
    """Send logs to the server"""
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        response = requests.post(
            LOGS_URL,
            json={"logs": logs},
            headers=headers
        )
        
        print(f"Send logs response: {response.status_code}")
        return response.json() if response.status_code in (200, 201) else None
    except Exception as e:
        print(f"Error sending logs: {str(e)}")
        return None

def list_server_logs(token):
    """List all log files on the server"""
    if not token:
        print("Authentication token required")
        return None
    
    try:
        response = requests.get(
            f"{LOGS_URL}list/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            return response.json()["files"]
        else:
            print(f"List logs failed: {response.status_code} {response.text}")
            return None
    except Exception as e:
        print(f"Error listing logs: {str(e)}")
        return None

def get_log_file(filename, token):
    """Get the content of a specific log file"""
    if not token:
        print("Authentication token required")
        return None
    
    try:
        response = requests.get(
            f"{LOGS_URL}{filename}/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            return response.json()["content"]
        else:
            print(f"Get log file failed: {response.status_code} {response.text}")
            return None
    except Exception as e:
        print(f"Error getting log file: {str(e)}")
        return None

def main():
    """Main test function"""
    parser = argparse.ArgumentParser(description="Test the LedgerLink logging API")
    parser.add_argument("--send", action="store_true", help="Send test logs to server")
    parser.add_argument("--list", action="store_true", help="List log files on server")
    parser.add_argument("--get", help="Get specific log file content by filename")
    parser.add_argument("--count", type=int, default=50, help="Number of logs to generate")
    parser.add_argument("--auth", action="store_true", help="Test with authentication")
    
    args = parser.parse_args()
    
    # Get auth token if needed
    token = None
    if args.auth:
        print("Getting authentication token...")
        token = get_auth_token()
        if not token:
            print("Failed to get authentication token. Exiting.")
            return
        
        print(f"Successfully authenticated")
    
    # Send logs
    if args.send:
        print(f"Generating {args.count} test logs...")
        logs = generate_test_logs(args.count)
        
        print(f"Sending logs to server...")
        result = send_logs_to_server(logs, token)
        
        if result:
            print(f"Successfully sent {result.get('log_count')} logs to {result.get('filename')}")
        else:
            print("Failed to send logs to server")
    
    # List logs
    if args.list:
        print("Listing log files on server...")
        files = list_server_logs(token)
        
        if files:
            print(f"Found {len(files)} log files:")
            for i, file in enumerate(files):
                print(f"{i+1}. {file['filename']} ({file['size']} bytes, created {file['created']})")
        else:
            print("Failed to list log files or no files found")
    
    # Get specific log file
    if args.get:
        print(f"Getting log file: {args.get}")
        content = get_log_file(args.get, token)
        
        if content:
            logs = content.get("logs", [])
            metadata = content.get("metadata", {})
            
            print(f"Log file details:")
            print(f"  Timestamp: {metadata.get('timestamp')}")
            print(f"  User: {metadata.get('user')}")
            print(f"  Log count: {metadata.get('log_count')}")
            print(f"  First 5 logs:")
            
            for i, log in enumerate(logs[:5]):
                print(f"    {i+1}. [{log.get('level')}] {log.get('message')}")
            
            if len(logs) > 5:
                print(f"    ... and {len(logs) - 5} more logs")
        else:
            print("Failed to get log file content")

if __name__ == "__main__":
    main()