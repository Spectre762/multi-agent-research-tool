import os
import shutil
import tempfile

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from orchestrator import Orchestrator

app = FastAPI(title="Multi-Provider Research Tool")

# Allow your future frontend (Vercel) to call this API from the browser.
# "*" is fine for local testing; narrow this to your actual frontend
# domain once you deploy.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    """Simple endpoint to confirm the server is running."""
    return {"status": "ok"}


@app.post("/research")
async def research(
    query: str = Form(...),
    provider: str = Form("claude"),
    document: UploadFile | None = File(None),
):
    """
    Run the full multi-agent research pipeline.

    - query: the research question
    - provider: which LLM powers the agents ("claude", "gemini", "openai")
    - document: optional file upload (PDF or .txt) for Document Agent
    """
    orchestrator = Orchestrator(provider_name=provider)

    document_path = None
    if document is not None:
        # Save the uploaded file to a temp location so DocumentAgent
        # (which expects a file path) can read it.
        suffix = os.path.splitext(document.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(document.file, tmp)
            document_path = tmp.name

    try:
        report = await orchestrator.run(query=query, document_path=document_path)
    finally:
        # Clean up the temp file regardless of success/failure
        if document_path and os.path.exists(document_path):
            os.remove(document_path)

    return {"report": report}
