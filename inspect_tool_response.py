"""Script to inspect the raw structure of Claude's tool use responses."""

import os
import json
from anthropic import Anthropic

# Simple tool definition
TOOLS = [
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
]

def inspect_response():
    """Make a call that will trigger tool use and inspect the response."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    client = Anthropic(api_key=api_key)

    print("=" * 70)
    print("SENDING REQUEST TO CLAUDE")
    print("=" * 70)
    print(f"Prompt: 'What's the weather in San Francisco?'")
    print(f"Tools provided: {json.dumps(TOOLS, indent=2)}")
    print()

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1024,
        tools=TOOLS,
        messages=[
            {"role": "user", "content": "What's the weather in San Francisco?"}
        ]
    )

    print("=" * 70)
    print("RAW RESPONSE STRUCTURE")
    print("=" * 70)
    print(f"\nResponse type: {type(response)}")
    print(f"\nResponse object attributes: {dir(response)}")
    print(f"\n--- STOP REASON ---")
    print(f"stop_reason: {response.stop_reason}")

    print(f"\n--- METADATA ---")
    print(f"id: {response.id}")
    print(f"model: {response.model}")
    print(f"role: {response.role}")
    print(f"type: {response.type}")

    print(f"\n--- USAGE ---")
    print(f"input_tokens: {response.usage.input_tokens}")
    print(f"output_tokens: {response.usage.output_tokens}")

    print(f"\n--- CONTENT BLOCKS ---")
    print(f"Number of content blocks: {len(response.content)}")
    print()

    for i, block in enumerate(response.content):
        print(f"Block {i}:")
        print(f"  Type: {block.type}")
        print(f"  Block object type: {type(block)}")
        print(f"  Block attributes: {dir(block)}")

        if block.type == "text":
            print(f"  Text content: {block.text}")
        elif block.type == "tool_use":
            print(f"  Tool name: {block.name}")
            print(f"  Tool use ID: {block.id}")
            print(f"  Tool input: {json.dumps(block.input, indent=4)}")
        print()

    print("=" * 70)
    print("CONVERTING TO DICT (if possible)")
    print("=" * 70)

    # Try to convert to dict to see the raw structure
    try:
        response_dict = response.model_dump()
        print(json.dumps(response_dict, indent=2, default=str))
    except Exception as e:
        print(f"Could not convert to dict: {e}")

if __name__ == "__main__":
    inspect_response()
