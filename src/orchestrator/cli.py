import typer
from pathlib import Path
from rich import print
from rich.table import Table
from src.orchestrator.dag import DAG, TaskNode
from src.orchestrator.lead import CoworkLead
from src.orchestrator.router import ModelRouter

app = typer.Typer(name="ag3", help="Antigravity 3.0 — Local multi-agent coding OS on deepseek-r1:8b")

@app.command()
def run(
    goal: str,
    auto_commit: bool = typer.Option(True, help="Auto-commit after each agent"),
    auto_yes: bool = typer.Option(True, help="Auto-accept aider changes"),
    dry_run: bool = typer.Option(False, help="Print actions without running aider")
):
    """Run Cowork Lead on a goal. Example: ag3 run 'Add /health endpoint'"""
    router = ModelRouter()
    if not router.check_ollama():
        print("[red]ERROR: Ollama not running. Start with `ollama serve`[/red]")
        raise typer.Exit(1)

    dag = DAG(goal=goal)
    t1 = TaskNode(name="architect", agent="architect", prompt=f"Plan: {goal}")
    t2 = TaskNode(name="senior_dev", agent="senior_dev", prompt=f"Implement: {goal}", depends_on=[t1.id])
    t3 = TaskNode(name="tester", agent="tester", prompt=f"Test: {goal}", depends_on=[t2.id])
    t4 = TaskNode(name="code_reviewer", agent="code_reviewer", prompt=f"Review: {goal}. Be strict and find at least 1 [NIT].", depends_on=[t3.id])
    for t in [t1, t2, t3, t4]:
        dag.add_node(t)

    lead = CoworkLead(dag, router, auto_commit=auto_commit, auto_yes=auto_yes)

    if dry_run:
        print("[yellow]DRY RUN: Would execute:[/yellow]")
        for node in dag.nodes.values():
            print(f" {node.agent}: {node.prompt}")
        raise typer.Exit()

    success = lead.run()
    if not success:
        raise typer.Exit(1)

@app.command()
def agents():
    """List 16 available agents and their models"""
    router = ModelRouter()
    table = Table(title="16 Agents — deepseek-r1:8b mode")
    table.add_column("Agent", style="cyan")
    table.add_column("Model", style="yellow")
    for agent, model in router.AGENT_MODEL_MAP.items():
        table.add_row(agent, model)
    print(table)

@app.command()
def serve(port: int = 8787):
    """Start Antigravity 3.0 Web Console"""
    import uvicorn
    print(f"[green]Starting AG3 Console at http://localhost:{port}[/green]")
    print("[green]All agents use deepseek-r1:8b[/green]")
    uvicorn.run("src.web.app:app", host="0.0.0.0", port=port, reload=False)

if __name__ == "__main__":
    app()