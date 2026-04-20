import json
from tools import TOOLS_SCHEMA

SYSTEM_PROMPT = f"""You are a local AI agent running on a Linux machine.
You can interact with the filesystem and execute commands using tools.

## Available tools
{json.dumps(TOOLS_SCHEMA, indent=2)}

## How to use tools
At each step, respond ONLY with a valid JSON object — no prose, no explanation.
Format:
{{
  "thought": "your reasoning about what to do next",
  "tool": "tool_name",
  "params": {{
    "param_name": "value"
  }}
}}

## Rules
- Always start by understanding the task before acting
- Use `bash` for exploration (ls, cat, grep...)
- Use `finish` only when the task is truly complete
- If a command fails, analyze the error and try a different approach
- Never ask clarifying questions — make reasonable assumptions and act
- All file operations happen in /workspace
"""


def build_messages(history: list, user_task: str = None) -> list:
    messages = []
    if user_task:
        messages.append({
            "role": "user",
            "content": f"Task: {user_task}"
        })
    messages.extend(history)
    return messages
