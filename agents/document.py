import os
from pypdf import PdfReader

from providers.factory import get_provider


class DocumentAgent:
    """
    extracts text from a PDF document and uses an LLM 
    to answer questions about it.
    """

    def __init__(self, provider_name: str = "gemini"):
        self.llm = get_provider(provider_name)

    def extract_text(self, file_path: str) -> str:
        """pull raw text from a PDF document"""

        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".pdf":
            reader = PdfReader(file_path)
            return "\n".join(page.extract_text() or "" for page in reader.pages)

        elif ext == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()

        else:
            raise ValueError(f"Unsupported file type: {ext}. Only PDF and TXT are supported.")


    async def run(self, file_path: str, question: str) -> str:
        """
        Extract text from a document and ask the LLM a question about it.
        """

        document_text = self.extract_text(file_path)

        if not document_text.strip():
            return "The document is empty or could not be read."

        prompt = (
            f"Based on the following document, answer this question: {question}\n\n"
            f"Document content:\n{document_text}\n\n"
            f"Provide a clear, well-organized answer citing which parts of the document support each claim."
            f"if the document does not contain relevant information, say 'The document does not contain relevant information.'"
        )

        response = await self.llm.generate(prompt=prompt)
        return response.text

