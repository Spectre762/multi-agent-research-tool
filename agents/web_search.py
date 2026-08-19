import os
from tavily import TavilyClient

from providers.factory import get_provider

class WebSearchAgent:
    """
    Searches the web using Tavily, then asks and LLM to summarize
    the result into one single answer
    """

    def __init__(self, provider_name: str = "gemini"):
        self.tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))
        self.llm = get_provider(provider_name)


    def search(self, query: str, max_results: int = 5) -> list[dict]:
        """
        Search the web using Tavily and return a list of URLs.
        """
        results = self.tavily.search(query=query, max_results=max_results)
        return results.get("results", [])

    async def run(self, query: str) -> str:
        """
        Search the web and summarize the results using the LLM.
        """
        raw_results = self.search(query)

        if not raw_results:
            return "No results found."

        #Build a plain text block the LLM can read
        sources_text = "\n\n".join(
            f"Source: {r['url']}\nTitle: {r['title']}\nContent: {r['content']}"
            for r in raw_results
        )

        prompt = (
            f"Based on the following web search results, answer this question: {query}\n\n"
            f"Search results:\n{sources_text}\n\n"
            f"Provide a clear, well-organized answer citing which sources support each claim."
        )

        response = await self.llm.generate(prompt=prompt)
        return response.text