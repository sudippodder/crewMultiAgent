import os
import requests
from crewai.tools import BaseTool
from typing import Type

class SerperTool(BaseTool):
    name: str = "serper_tool"
    description: str = "Search the web using the Serper API and return summarized snippets."

    def _run(self, query: str) -> str:
        """Run the tool with a given query."""
        api_key = os.getenv("SERPER_API_KEY")
        if not api_key:
            return "Error: SERPER_API_KEY not found in environment variables."

        url = "https://serper.dev/api/search"
        headers = {"X-API-KEY": api_key}
        payload = {"q": query}
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            return f"Serper API request failed: {e}"

        data = response.json()
        snippets = [r.get("snippet", "") for r in data.get("organic", [])]
        return "\n".join(snippets) if snippets else "No results found."
