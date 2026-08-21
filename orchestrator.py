from agents.web_search import WebSearchAgent
from agents.document import DocumentAgent
from agents.synthesis import SynthesisAgent


class Orchestrator:
    """
    Decides which agents to run for a given query, runs them,
    and passes their findings to the Synthesis Agent.
    """

    def __init__(self, provider_name: str = "gemini"):
        self.provider_name = provider_name
        self.search_agent = WebSearchAgent(provider_name=provider_name)
        self.doc_agent = DocumentAgent(provider_name=provider_name)
        self.synth_agent = SynthesisAgent(provider_name=provider_name)

    async def run(
        self, 
        query: str, 
        document_path: str | None = None, 
        document_text: str | None = None
    ) -> str:
        """
        Runs the appropriate agents based on what's available, then synthesizes.

        - Always runs Web Search Agent using the short clean user query.
        - Runs Document Agent if a document_path is provided.
        - Injects raw document_text directly into findings if provided.
        - Passes findings to Synthesis Agent for final report generation.
        """
        findings = {}

        # 1. Web search receives ONLY the short original query (prevents Tavily >1500 char crash)
        findings["web_search"] = await self.search_agent.run(query)

        # 2. Extract context from file path if DocumentAgent is used
        if document_path:
            try:
                findings["document"] = await self.doc_agent.run(document_path, query)
            except Exception as e:
                print(f"DocumentAgent Warning: {e}")

        # 3. Direct PDF text injection context override/supplement
        if document_text:
            existing_doc = findings.get("document", "")
            findings["document"] = f"{existing_doc}\n\n[Extracted Document Content]:\n{document_text}".strip()

        # 4. Pass compiled findings to Synthesis Agent
        final_report = await self.synth_agent.run(query, findings)
        return final_report