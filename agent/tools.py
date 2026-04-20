import subprocess
import os

WORKSPACE = "/workspace"

# --- Définition des outils exposés au LLM ---
# C'est ce JSON que tu enverras au LLM pour qu'il sache quoi demander

TOOLS_SCHEMA = [
    {
        "name": "bash",
        "description": "Execute a bash command. Working directory is /workspace. Use for ls, cat, mkdir, running scripts, etc.",
        "parameters": {
            "cmd": "string — the bash command to execute"
        }
    },
    {
        "name": "read_file",
        "description": "Read the content of a file in /workspace.",
        "parameters": {
            "path": "string — relative path from /workspace"
        }
    },
    {
        "name": "finish",
        "description": "Call this when the task is fully completed. Provide a summary of what was done.",
        "parameters": {
            "summary": "string — what was accomplished"
        }
    }
]


def execute_tool(tool_name: str, params: dict) -> str:
    """Reçoit la décision du LLM et l'exécute réellement."""

    if tool_name == "bash":
        return _run_bash(params.get("cmd", ""))
    if tool_name == "read_file":
        return _read_file(params.get("path", ""))
    if tool_name == "finish":
        return f"FINISH:{params.get('summary', 'Task completed.')}"
    return f"ERROR: Unknown tool '{tool_name}'"


def _run_bash(cmd: str) -> str:
    if not cmd:
        return "ERROR: empty command"
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=WORKSPACE
        )
        output = result.stdout + result.stderr
        return output[:3000] if output else "(no output)"
    except subprocess.TimeoutExpired:
        return "ERROR: command timed out after 30s"
    except Exception as e:
        return f"ERROR: {e}"


def _read_file(path: str) -> str:
    if not path:
        return "ERROR: empty path"
    full_path = os.path.join(WORKSPACE, path.lstrip("/"))
    if not os.path.exists(full_path):
        return f"ERROR: file not found: {full_path}"
    with open(full_path, "r") as f:
        content = f.read()
    return content[:3000]
