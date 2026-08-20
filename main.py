import io
import os
import tempfile
import traceback
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

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
        
        # 1. Extract text from PDF safely
        if uploaded_file.filename.lower().endswith(".pdf") and PdfReader is not None:
            try:
                pdf_reader = PdfReader(io.BytesIO(file_bytes))
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text:
                        pdf_text += text + "\n"
            except Exception as e:
                print(f"PDF Extraction Error: {e}")

        # 2. Save byte stream to disk for downstream agents
        suffix = os.path.splitext(uploaded_file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(file_bytes)
            document_path = tmp.name

    # Truncate raw document text so it stays within manageable context limits
    doc_context = pdf_text.strip()[:4000] if pdf_text.strip() else None

    orchestrator = Orchestrator(provider_name=provider)

    try:
        # Pass the original short query for Tavily, and pass doc_context separately
        report = await orchestrator.run(
            query=query, 
            document_path=document_path,
            document_text=doc_context
        )
    except Exception as e:
        print("Backend Error Traceback:\n", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Pipeline Error: {str(e)}")
    finally:
        if document_path and os.path.exists(document_path):
            os.remove(document_path)

    return {"report": report}
