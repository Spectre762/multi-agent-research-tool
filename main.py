import io
import os
import shutil
import tempfile
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader

from orchestrator import Orchestrator

app = FastAPI(title="Multi-Provider Research Tool")

# Enable CORS for Next.js frontend
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
    # Changed parameter name to 'file' (or alias) so it matches Next.js FormData
    file: UploadFile | None = File(None, alias="file"),
    document: UploadFile | None = File(None)
):
    """
    Run the full multi-agent research pipeline.

    - query: the research question
    - provider: which LLM powers the agents ("claude", "gemini", "openai")
    - file / document: optional file upload (PDF or .txt)
    """
    # Accept either 'file' or 'document' key from incoming FormData
    uploaded_file = file or document
    document_path = None
    pdf_text = ""

    if uploaded_file is not None and uploaded_file.filename:
        # 1. Parse PDF text directly into prompt context
        if uploaded_file.filename.lower().endswith(".pdf"):
            try:
                pdf_bytes = await uploaded_file.read()
                pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text:
                        pdf_text += text + "\n"
                await uploaded_file.seek(0)  # Reset stream position for disk write
            except Exception as e:
                print(f"PDF extraction error: {e}")

        # 2. Save temp file for Orchestrator/DocumentAgent file-path compatibility
        suffix = os.path.splitext(uploaded_file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(uploaded_file.file, tmp)
            document_path = tmp.name

    # Prepend extracted text to the query context if available
    final_query = query
    if pdf_text.strip():
        final_query = f"[Document Content:\n{pdf_text.strip()[:6000]}]\n\nUser Question: {query}"

    orchestrator = Orchestrator(provider_name=provider)

    try:
        report = await orchestrator.run(query=final_query, document_path=document_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temp file
        if document_path and os.path.exists(document_path):
            os.remove(document_path)

    return {"report": report}
