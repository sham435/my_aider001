import subprocess
from pathlib import Path
from typing import Dict

# All 16 agents mapped to deepseek-r1:8b for low-storage mode
AGENT_MODEL_MAP: Dict[str, str] = {
    "architect": "ollama/deepseek-r1:8b",
    "senior_dev": "ollama/deepseek-r1:8b",
    "code_reviewer": "ollama/deepseek-r1:8b",
    "devops": "ollama/deepseek-r1:8b",
    "tester": "ollama/deepseek-r1:8b",
    "debugger": "ollama/deepseek-r1:8b",
    "refactorer": "ollama/deepseek-r1:8b",
    "docs_writer": "ollama/deepseek-r1:8b",
    "security": "ollama/deepseek-r1:8b",
    "data_engineer": "ollama/deepseek-r1:8b",
    "frontend": "ollama/deepseek-r1:8b",
    "performance": "ollama/deepseek-r1:8b",
    "pm": "ollama/deepseek-r1:8b",
    "researcher": "ollama/deepseek-r1:8b",
    "fast_editor": "ollama/deepseek-r1:8b",
    "cowork_lead": "ollama/deepseek-r1:8b",
}

class ModelRouter:
    def __init__(self, prompts_dir: Path = Path(".aider/prompts/agents")):
        self.prompts_dir = prompts_dir

    def get_prompt_path(self, agent: str) -> Path:
        files = list(self.prompts_dir.glob(f"*_{agent}.md"))
        if not files:
            raise ValueError(f"No prompt file for agent: {agent}")
        return files[0]

    def get_model(self, agent: str) -> str:
        return AGENT_MODEL_MAP.get(agent, "ollama/deepseek-r1:8b")

    def check_ollama(self) -> bool:
        try:
            subprocess.run(["ollama", "list"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False