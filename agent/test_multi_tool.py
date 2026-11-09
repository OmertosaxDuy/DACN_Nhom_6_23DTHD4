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


def get_ip_sessions(src_ip: str):
    response = requests.get(
        f"{TOOL_API_BASE_URL}/ips/{src_ip}/sessions",
        headers=HEADERS,
        timeout=10,
    )

    response.raise_for_status()

    data = response.json()
    sessions = data.get("sessions", [])

    root_sessions = [
        s for s in sessions
        if s.get("username") == "root"
    ]

    latest_root_session_id = (
        root_sessions[0]["session_id"]
          if root_sessions
          else None
    )

    recent_sessions = sessions[:5]

    return {
        "src_ip": src_ip,
        "session_count": len(sessions),
        "root_session_count": len(root_sessions),
        "recent_sessions": recent_sessions,
        "latest_root_session_id": latest_root_session_id,
    }

def get_session_activity(session_id: str):
    recent_response = requests.get(
        f"{TOOL_API_BASE_URL}/sessions/{session_id}/recent",
        headers=HEADERS,
        params={"limit": 5},
        timeout=10,
    )

    recent_response.raise_for_status()
    recent_data = recent_response.json()

    command_response = requests.get(
        f"{TOOL_API_BASE_URL}/sessions/{session_id}/commands",
        headers=HEADERS,
        timeout=10,
    )

    command_response.raise_for_status()
    command_data = command_response.json()

    commands = command_data.get("commands", [])

    return {
        "session_id": session_id,
        "recent_events": recent_data.get("events", [])[:5],
        "recent_commands": commands[:5],
        "command_count": command_data.get(
            "command_count",
            len(commands)
        ),
    }

tools = [
    {
        "type": "function",
        "function": {
            "name": "check_bruteforce",
            "description": (
                "Check whether a source IP is performing "
                "SSH brute-force activity."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "src_ip": {
                        "type": "string"
                    }
                },
                "required": ["src_ip"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_ip_sessions",
            "description": (
                "Get a compact summary of honeypot sessions "
                "associated with a source IP."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "src_ip": {
                        "type": "string"
                    }
                },
                "required": ["src_ip"]
            }
        }
    },
    {
    "type": "function",
    "function": {
        "name": "get_session_activity",
        "description": (
            "Inspect recent commands and events from a specific "
            "honeypot session."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "string",
                    "description": "Honeypot session ID"
                }
            },
            "required": ["session_id"]
        }
    }
}
]

TOOL_FUNCTIONS = {
    "check_bruteforce": check_bruteforce,
    "get_ip_sessions": get_ip_sessions,
    "get_session_activity": get_session_activity,
}


messages = [
    {
        "role": "system",
        "content": (
            "You are a Cyber Deception AI Agent operating only "
            "inside an authorized honeypot lab. "
            "Use tools to verify evidence. "
            "First check whether the IP is performing brute force. "
            "If brute force is detected, inspect the IP sessions. "
            "If a root session is available, inspect that session's "
            "recent activity before giving the final assessment. "
            "Do not invent facts."
        ),
    },
    {
        "role": "user",
        "content": (
            "Investigate suspicious activity from source IP "
            "192.168.255.130. Determine whether it is brute force "
            "and whether the IP has honeypot sessions."
        ),
    },
]


MAX_TOOL_CALLS = 3
tool_call_count = 0


while tool_call_count < MAX_TOOL_CALLS:
    response = ollama.chat(
        model="qwen3:4b",
        messages=messages,
        tools=tools,
        think=False,
    )

    assistant_message = response["message"]
    tool_calls = assistant_message.get("tool_calls", [])

    if not tool_calls:
        print("\nFinal model decision:")
        print(assistant_message.get("content", ""))
        break

    messages.append(assistant_message)

    for tool_call in tool_calls:
        if tool_call_count >= MAX_TOOL_CALLS:
            break

        function_name = tool_call["function"]["name"]
        arguments = tool_call["function"]["arguments"]

        print("\nTool selected:")
        print(function_name)

        print("\nArguments:")
        print(json.dumps(arguments, indent=2))

        if function_name not in TOOL_FUNCTIONS:
            result = {
                "error": "Tool not allowed"
            }
        else:
            try:
                result = TOOL_FUNCTIONS[function_name](**arguments)
            except Exception as exc:
                result = {
                    "error": str(exc)
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

        tool_call_count += 1

else:
    print("\nMaximum tool-call limit reached.")

    messages.append(
    {
        "role": "user",
        "content": (
            "/no_think\n"
            "Using only the exact tool results above, return exactly "
            "three lines:\n"
            "Bruteforce: <true/false and evidence>\n"
            "Sessions: <session_count and root_session_count>\n"
            "Assessment: <one cautious conclusion>\n"
            "Do not infer usernames, credential stuffing, attacker intent, "
            "or any fact not explicitly present in the tool results."
        ),
    }
)

    final_response = ollama.chat(
        model="qwen3:4b",
        messages=messages,
        think=False,
    )

    print("\nFinal model decision:")
    content = final_response["message"]["content"]

if "</think>" in content:
    content = content.split("</think>", 1)[1].strip()

print(content)
