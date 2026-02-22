#!/usr/bin/env python3
"""
Send a test message to ChatKit endpoint using the correct format.
"""

import requests
import json

BACKEND_URL = "http://localhost:8005"

# Step 1: Create a thread
print("Step 1: Creating thread...")
create_thread_request = {
    "type": "threads.create",
    "params": {}
}

response = requests.post(
    f"{BACKEND_URL}/chatkit",
    headers={
        "Content-Type": "application/json",
        "X-User-ID": "test_user_123"
    },
    json=create_thread_request
)

print(f"Response status: {response.status_code}")
if response.status_code != 200:
    print(f"Error: {response.text}")
    exit(1)

thread_data = response.json()
thread_id = thread_data.get("id")
print(f"Thread created: {thread_id}")
print("-" * 80)

# Step 2: Add user message
print("Step 2: Adding user message...")
add_message_request = {
    "type": "threads.add_user_message",
    "thread_id": thread_id,
    "message": {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "Add a task to buy milk"
            }
        ]
    }
}

print(f"Request: {json.dumps(add_message_request, indent=2)}")
print("-" * 80)

response = requests.post(
    f"{BACKEND_URL}/chatkit",
    headers={
        "Content-Type": "application/json",
        "X-User-ID": "test_user_123"
    },
    json=add_message_request,
    stream=True
)

print(f"Response status: {response.status_code}")
print("-" * 80)

if response.status_code == 200:
    print("Response (streaming):")
    for line in response.iter_lines():
        if line:
            decoded = line.decode('utf-8')
            print(decoded)
else:
    print(f"Error: {response.text}")

print("\n" + "=" * 80)
print("CHECK backend_live.log FOR DETAILED EXECUTION TRACE")
print("=" * 80)
