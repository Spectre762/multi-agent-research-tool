from providers.factory import get_provider

class SynthesisAgent:
    """
    Combines multiple LLM providers to generate a single answer.
    """

    def __init__(self, provider_name: str = "gemini"):
        self.llm = get_provider(provider_name)

    async def run(self, query: str, findings: dict[str, str]) -> str:
        """
        Synthesize findings from multiple sources into a single answer.
        """

        findings_text = "\n\n".join(
            f"--- Findings from {name} ---\n{content}"
            for name, content in findings.items()
        )

        prompt = (
            f"You are combining research findings from multiple sources to answer "
            f"this question: {query}\n\n"
            f"{findings_text}\n\n"
            f"Write a single, well-organized report that synthesizes all of this "
            f"into a clear answer. Resolve any contradictions between sources by "
            f"noting them explicitly. Do not simply list each source separately — "
            f"weave them into one coherent narrative."
        )

        response = await self.llm.generate(prompt=prompt)
        return response.text