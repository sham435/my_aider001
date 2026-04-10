from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Antigravity 3.0 Console")

@app.get("/")
async def root():
    return HTMLResponse("""
    <h1>Antigravity 3.0</h1>
    <p>Local multi-agent coding OS running on deepseek-r1:8b</p>
    <p>Repo: <a href="https://github.com/sham435/my_aider001">github.com/sham435/my_aider001</a></p>
    <p>CLI: Run <code>ag3 serve</code> locally for full DAG UI</p>
    """)

@app.get("/health")
async def health():
    return {"status": "ok", "model": "deepseek-r1:8b"}