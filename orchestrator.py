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

    async def run(self, query: str, document_path: str | None = None) -> str:
        """
        Runs the appropriate agents based on what's available, then synthesizes.

        - Always runs Web Search Agent.
        - Runs Document Agent only if a document_path is provided.
        - Passes everything to Synthesis Agent for the final report.
        """
        findings = {}

        # Always search the web
        findings["web_search"] = await self.search_agent.run(query)

        # Only read a document if one was provided
        if document_path:
            findings["document"] = await self.doc_agent.run(document_path, query)

        # If only one agent ran, no real synthesis needed — but we still
        # pass through Synthesis Agent for consistent formatting.
        final_report = await self.synth_agent.run(query, findings)
        return final_report
