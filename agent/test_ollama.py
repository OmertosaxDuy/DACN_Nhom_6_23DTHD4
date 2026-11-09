import ollama

response = ollama.chat(
    model="qwen3:4b",
    messages=[
        {
            "role": "system",
            "content": (
                "You are a Cyber Deception AI Agent operating "
                "only inside an authorized honeypot lab. "
                "Analyze only the evidence provided. "
                "Do not invent facts."
            ),
        },
        {
            "role": "user",
            "content": (
                "Observation: source IP 192.168.255.130 "
                "failed SSH login 20 times and later executed "
                "'uname -a'. Analyze briefly."
            ),
        },
    ],
)

print(response["message"]["content"])
