import io
import os
import tempfile
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Ensure pypdf is imported safely
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

from orchestrator import Orchestrator

app = FastAPI(title="Multi-Provider Research Tool")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "ok"}

@app.post("/research")
async def research(
    query: str = Form(...),
    provider: str = Form("claude"),
    file: UploadFile | None = File(None, alias="file"),
    document: UploadFile | None = File(None)
):
    uploaded_file = file or document
    document_path = None
    pdf_text = ""

    if uploaded_file is not None and uploaded_file.filename:
        file_bytes = await uploaded_file.read()
        
        # 1. Extract text if PDF
        if uploaded_file.filename.lower().endswith(".pdf") and PdfReader is not None:
            try:
                pdf_reader = PdfReader(io.BytesIO(file_bytes))
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text:
                        pdf_text += text + "\n"
            except Exception as e:
                print(f"PDF Parsing Warning: {e}")

        # 2. Save byte stream to disk for downstream agents
        suffix = os.path.splitext(uploaded_file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(file_bytes)
            document_path = tmp.name

    # Build prompt context
    final_query = query
    if pdf_text.strip():
        final_query = f"[Document Context:\n{pdf_text.strip()[:6000]}]\n\nUser Question: {query}"

    orchestrator = Orchestrator(provider_name=provider)

    try:
        report = await orchestrator.run(query=final_query, document_path=document_path)
    except Exception as e:
        print(f"Execution Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if document_path and os.path.exists(document_path):
            os.remove(document_path)

    return {"report": report}
