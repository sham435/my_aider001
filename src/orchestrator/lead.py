import subprocess
from pathlib import Path
from typing import List
from rich import print
from src.orchestrator.dag import DAG, TaskNode, TaskStatus
from src.orchestrator.router import ModelRouter

def get_git_touched_files(base_commit: str) -> List[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", base_commit, "HEAD"],
        capture_output=True, text=True, check=True
    )
    return [f for f in result.stdout.splitlines() if f]

def get_last_commit_hash() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True
    )
    return result.stdout.strip()

class CoworkLead:
    def __init__(self, dag: DAG, router: ModelRouter, auto_commit: bool = True, auto_yes: bool = True):
        self.dag = dag
        self.router = router
        self.auto_commit = auto_commit
        self.auto_yes = auto_yes
        self.base_commit = get_last_commit_hash()

    def _run_aider(self, agent: str, model: str, prompt: str) -> bool:
        prompt_path = self.router.get_prompt_path(agent)
        cmd = [
            "aider",
            "--model", model,
            "--read", str(prompt_path),
            "--message", prompt,
            "--yes",
        ]
        if self.auto_commit:
            cmd.append("--auto-commits")

        print(f"[LEAD] Exec: {' '.join(cmd)}")
        before = get_last_commit_hash()
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"[red]AIDER ERROR[/red]: {result.stderr}")
            return False

        print(result.stdout)
        after = get_last_commit_hash()
        return before != after

    def delegate(self, node: TaskNode) -> bool:
        model = self.router.get_model(node.agent)
        print(f"[LEAD] -> {node.agent} [{model}]")
        print(f"[LEAD] Task: {node.name}")

        success = self._run_aider(node.agent, model, node.prompt)
        if not success:
            print(f"[red]BLOCKED: {node.name} failed[/red]")
            node.status = TaskStatus.BLOCKED
        return success

    def run(self) -> bool:
        print(f"[LEAD] Starting Cowork: {self.dag.goal}")
        print(f"[LEAD] Auto-commit: {self.auto_commit}, Auto-yes: {self.auto_yes}")

        if not self.router.check_ollama():
            print("[red]ERROR: Ollama not running. Start with `ollama serve`[/red]")
            return False

        while not self.dag.all_done():
            node = self.dag.next_runnable()
            if not node:
                print("[red]DAG BLOCKED: No runnable tasks, but not all done[/red]")
                return False

            node.status = TaskStatus.RUNNING
            if not self.delegate(node):
                return False

            touched = get_git_touched_files(self.base_commit)
            self.dag.mark_done(node.id, touched)
            print(f"[green]DONE: {node.name}[/green] Files: {touched}")
            self.base_commit = get_last_commit_hash()

        print("[LEAD] All tasks complete. Cowork finished.")
        return True