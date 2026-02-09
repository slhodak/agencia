"""Make raw HTTP requests to see the actual wire format of Claude API calls."""

import os
import json
import requests

def make_raw_request():
    """Make a raw HTTP request to the Claude API."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    # The actual API endpoint
    url = "https://api.anthropic.com/v1/messages"

    # Headers
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }

    # Request body
    request_body = {
        "model": "claude-sonnet-4-5-20250929",
        "max_tokens": 1024,
        "tools": [
            {
                "name": "get_weather",
                "description": "Get the weather for a location",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA"
                        }
                    },
                    "required": ["location"]
                }
            }
        ],
        "messages": [
            {
                "role": "user",
                "content": "What's the weather in San Francisco?"
            }
        ]
    }

    print("=" * 80)
    print("RAW HTTP REQUEST")
    print("=" * 80)
    print(f"\nURL: {url}")
    print(f"\nHeaders:")
    # Mask the API key for security
    display_headers = headers.copy()
    display_headers["x-api-key"] = api_key[:8] + "..." + api_key[-4:]
    print(json.dumps(display_headers, indent=2))
    print(f"\nRequest Body:")
    print(json.dumps(request_body, indent=2))

    print("\n" + "=" * 80)
    print("SENDING REQUEST...")
    print("=" * 80)

    # Make the request
    response = requests.post(url, headers=headers, json=request_body)

    print("\n" + "=" * 80)
    print("RAW HTTP RESPONSE")
    print("=" * 80)
    print(f"\nStatus Code: {response.status_code}")
    print(f"\nResponse Headers:")
    print(json.dumps(dict(response.headers), indent=2))
    print(f"\nResponse Body:")
    response_json = response.json()
    print(json.dumps(response_json, indent=2))

    print("\n" + "=" * 80)
    print("ANALYSIS")
    print("=" * 80)
    print(f"\nNotice how Claude's response includes:")
    print(f"  - stop_reason: '{response_json.get('stop_reason')}'")
    print(f"  - content blocks: {len(response_json.get('content', []))} block(s)")

    for i, block in enumerate(response_json.get('content', [])):
        print(f"\n  Block {i}:")
        print(f"    - type: '{block.get('type')}'")
        if block.get('type') == 'tool_use':
            print(f"    - name: '{block.get('name')}'")
            print(f"    - id: '{block.get('id')}'")
            print(f"    - input: {json.dumps(block.get('input'), indent=6)}")

if __name__ == "__main__":
    make_raw_request()
