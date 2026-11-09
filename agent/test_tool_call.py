import os
import json
import requests
import ollama

TOOL_API_BASE_URL = "http://localhost:8000"
API_KEY = os.environ["TOOL_API_KEY"]

HEADERS = {
    "X-API-Key": API_KEY
}


def check_bruteforce(src_ip: str):
    response = requests.get(
        f"{TOOL_API_BASE_URL}/ips/{src_ip}/bruteforce",
        headers=HEADERS,
        timeout=10,
    )

    response.raise_for_status()
    return response.json()


tools = [
    {
        "type": "function",
        "function": {
            "name": "check_bruteforce",
            "description": (
                "Check whether a source IP is performing "
                "SSH brute-force activity using honeypot data."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "src_ip": {
                        "type": "string",
                        "description": "Source IP address to investigate"
                    }
                },
                "required": ["src_ip"]
            }
        }
    }
]


messages = [
    {
        "role": "system",
        "content": (
            "You are a Cyber Deception AI Agent operating only "
            "inside an authorized honeypot lab. "
            "Use available tools when evidence should be verified. "
            "Do not invent facts."
        ),
    },
    {
        "role": "user",
        "content": (
            "Suspicious activity was observed from 192.168.255.130. "
            "Determine whether this IP is performing SSH brute force. "
            "Use the available tool if needed."
        ),
    },
]


print("Sending observation to Qwen...")

response = ollama.chat(
    model="qwen3:4b",
    messages=messages,
    tools=tools,
)

assistant_message = response["message"]

print("\nInitial model response:")
print(assistant_message.get("content", ""))


tool_calls = assistant_message.get("tool_calls", [])

if not tool_calls:
    print("\nModel did not call a tool.")
else:
    messages.append(assistant_message)

    for tool_call in tool_calls:
        function_name = tool_call["function"]["name"]
        arguments = tool_call["function"]["arguments"]

        print("\nTool selected:")
        print(function_name)

        print("\nArguments:")
        print(json.dumps(arguments, indent=2))

        if function_name == "check_bruteforce":
            result = check_bruteforce(
                arguments["src_ip"]
            )
        else:
            result = {
                "error": "Tool not allowed"
            }

        print("\nTool result:")
        print(json.dumps(result, indent=2))

        messages.append(
            {
                "role": "tool",
                "tool_name": function_name,
                "content": json.dumps(result),
            }
        )

    final_response = ollama.chat(
        model="qwen3:4b",
        messages=messages,
        tools=tools,
    )

    print("\nFinal model decision:")
    print(final_response["message"]["content"])
