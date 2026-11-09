import json
import re


class AnalysisAgent:
    def __init__(self, llm_client=None, model="qwen3:1.7b"):
        self.llm_client = llm_client
        self.model = model

    def _extract_json(self, text: str) -> dict:
        text = text.strip()

        # bỏ markdown fence nếu model tự sinh
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end == -1:
            raise ValueError("LLM did not return JSON")

        return json.loads(text[start:end + 1])

    def analyze(self, observation: dict) -> dict:
        facts = observation.get("derived_facts", {})

        commands = facts.get("recent_attacker_commands", [])

        if not commands:
            commands = observation.get("recent_attacker_commands", [])

        # fallback nếu observation lưu commands ở key khác
        if not commands:
            commands = observation.get("commands", [])

        # Không có LLM thì vẫn trả object hợp lệ
        if not self.llm_client or not commands:
            return {
                "evidence": [],
                "facts": facts,
                "evidence_count": 0,
                "command_analysis": [],
            }

        command_text = "\n".join(
            f"{i + 1}. {cmd}"
            for i, cmd in enumerate(commands)
        )

        prompt = f"""
You are a cybersecurity behavior classifier analyzing commands
executed by an attacker inside an SSH honeypot.

Analyze EVERY command below independently.

Observed commands:
{command_text}

Classify behavior based on semantic meaning, not exact filenames.

Possible behavior categories include:

- system_discovery
- account_discovery
- file_discovery
- database_discovery
- credential_discovery
- cloud_discovery
- network_discovery
- download_attempt
- execution
- persistence
- privilege_discovery
- benign_or_unknown

Important rules:

1. Do not invent commands.
2. Only classify behavior supported by the observed commands.
3. A command may have multiple behaviors.
4. Reading database configuration or database connection information
   should count as database_discovery.
5. Searching for or reading authentication material, passwords,
   credentials or secrets should count as credential_discovery.
6. Searching for or reading cloud access information should count
   as cloud_discovery.
7. wget/curl or similar remote retrieval attempts should count as
   download_attempt even if the download fails.
8. Commands such as whoami, id, hostname, uname and pwd should be
   classified according to their reconnaissance/discovery semantics.
9. Routine shell control commands such as exit, logout, clear, or cd
   without suspicious context should be marked suspicious=false.
10. A command may have no behavior classification if it is benign or
    only controls the shell session.
11. Analyze EVERY input command exactly once.
    Do not skip, merge, or omit any command.
    The command_analysis array must contain the same number
    of entries as the input command list.


Return JSON ONLY in exactly this structure:

{{
  "detected_behaviors": [
    "behavior_name"
  ],

  "other_behaviors": [],

  "suspicious_command_count": 0,

  "overall_confidence": 0.0,

  "command_analysis": [
    {{
      "command": "original command",
      "behaviors": ["behavior_name"],
      "suspicious": true,
      "confidence": 0.0,
      "reason": "short explanation"
    }}
  ]
}}
"""

        response = self.llm_client.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            format="json",
            options={
                "temperature": 0,
            },
        )

        content = response["message"]["content"]

        semantic = self._extract_json(content)

        # Merge semantic facts vào deterministic facts
        merged_facts = dict(facts)

        raw_detected_behaviors = semantic.get(
             "detected_behaviors",
             [],
        )

        detected_behaviors = list(
             dict.fromkeys(
                  raw_detected_behaviors
             )
        )

        command_analysis = semantic.get(
            "command_analysis",
            [],
        )

        for item in command_analysis:
           behaviors = item.get(
              "behaviors",
              [],
           )

           item["suspicious"] = any(
              behavior != "benign_or_unknown"
              for behavior in behaviors
           )

        suspicious_command_count = sum(
          1
          for item in command_analysis
          if item.get("suspicious") is True
        )

        merged_facts[
             "detected_behaviors"
        ] = detected_behaviors

        merged_facts[
             "other_behaviors"
        ] = semantic.get(
             "other_behaviors",
             [],
        )

        merged_facts[
              "suspicious_command_count"
        ] = suspicious_command_count

        merged_facts[
              "overall_confidence"
        ] = semantic.get(
              "overall_confidence",
              0.0,
        )

        evidence = list(detected_behaviors)

        other_behaviors = semantic.get(
             "other_behaviors",
             [],
        )

        evidence.extend(other_behaviors)

        return {
            "evidence": evidence,
            "facts": merged_facts,
            "evidence_count": len(evidence),
            "command_analysis": semantic.get(
                "command_analysis", []
            ),
        }
