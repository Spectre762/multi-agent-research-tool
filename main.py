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
    files: list[UploadFile] = File(default=[]),
    file: UploadFile | None = File(None, alias="file"),
    document: UploadFile | None = File(None)
):
    # Consolidate single file fallbacks with the list of files
    all_uploads = list(files)
    if file:
        all_uploads.append(file)
    if document:
        all_uploads.append(document)

    combined_pdf_text = ""
    temp_paths = []

    for uploaded_file in all_uploads:
        if not uploaded_file.filename:
            continue

        file_bytes = await uploaded_file.read()

        # 1. Extract text if the file is a PDF
        if uploaded_file.filename.lower().endswith(".pdf") and PdfReader is not None:
            try:
                pdf_reader = PdfReader(io.BytesIO(file_bytes))
                extracted_pages = []
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text:
                        extracted_pages.append(text)
                
                doc_text = "\n".join(extracted_pages)
                if doc_text.strip():
                    combined_pdf_text += f"\n--- Document: {uploaded_file.filename} ---\n{doc_text.strip()}\n"
            except Exception as e:
                print(f"Error parsing PDF {uploaded_file.filename}: {e}")

        # 2. Save byte stream to temp disk file for downstream agent compatibility
        try:
            suffix = os.path.splitext(uploaded_file.filename)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(file_bytes)
                temp_paths.append(tmp.name)
        except Exception as e:
            print(f"Error writing temp file for {uploaded_file.filename}: {e}")

    # Truncate total concatenated text to remain within reasonable LLM context limits
    doc_context = combined_pdf_text.strip()[:8000] if combined_pdf_text.strip() else None
    primary_doc_path = temp_paths[0] if temp_paths else None

    orchestrator = Orchestrator(provider_name=provider)

    try:
        report = await orchestrator.run(
            query=query,
            document_path=primary_doc_path,
            document_text=doc_context
        )
    except Exception as e:
        print("Backend Error Traceback:\n", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Pipeline Error: {str(e)}")
    finally:
        # Clean up all created temporary files
        for path in temp_paths:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except Exception as cleanup_err:
                    print(f"Failed to remove temp file {path}: {cleanup_err}")

    return {"report": report}
