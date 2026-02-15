#!/usr/bin/env python3
"""
Simple HTTP client to send a test message to the backend.
This will trigger the tracing in the server.
"""

import requests
import json
import time

# Backend URL
BACKEND_URL = "http://localhost:8000"

def send_chat_message(message: str, user_id: str = "test_user_123"):
    """Send a chat message to the backend."""

    print(f"Sending message: {message}")
    print(f"User ID: {user_id}")
    print("-" * 80)

    # Create a new thread
    create_thread_response = requests.post(
        f"{BACKEND_URL}/threads",
        headers={"X-User-ID": user_id}
    )

    if create_thread_response.status_code != 200:
        print(f"Failed to create thread: {create_thread_response.status_code}")
        print(create_thread_response.text)
        return

    thread_data = create_thread_response.json()
    thread_id = thread_data.get("id")
    print(f"Created thread: {thread_id}")

    # Send message
    send_message_response = requests.post(
        f"{BACKEND_URL}/threads/{thread_id}/messages",
        headers={"X-User-ID": user_id},
        json={"content": message}
    )

    if send_message_response.status_code != 200:
        print(f"Failed to send message: {send_message_response.status_code}")
        print(send_message_response.text)
        return

    print(f"Message sent successfully!")
    print("-" * 80)
    print("Response:")
    print(send_message_response.text)
    print("-" * 80)

    # Wait a bit for processing
    time.sleep(2)

    # Get thread messages to see the result
    get_messages_response = requests.get(
        f"{BACKEND_URL}/threads/{thread_id}/messages",
        headers={"X-User-ID": user_id}
    )

    if get_messages_response.status_code == 200:
        messages = get_messages_response.json()
        print(f"\nThread messages ({len(messages)} total):")
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", [])
            if content and len(content) > 0:
                text = content[0].get("text", "")
                print(f"  [{role}]: {text[:200]}")

    return thread_id

if __name__ == "__main__":
    print("="*80)
    print("SENDING TEST MESSAGE TO BACKEND")
    print("="*80)
    print()

    # Send test message
    thread_id = send_chat_message("Add a task to buy milk")

    print()
    print("="*80)
    print("CHECK THE BACKEND SERVER LOGS FOR TRACE OUTPUT")
    print("="*80)
