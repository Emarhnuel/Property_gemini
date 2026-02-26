from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from exa_py import Exa
import os


class ExaSearchToolInput(BaseModel):
    """Input schema for ExaSearchTool."""
    query: str = Field(..., description="The highly descriptive search string to send to Exa.")

class ExaSearchTool(BaseTool):
    name: str = "exa_search"
    description: str = (
        "A search engine optimized for AI agents. "
        "Useful to search the internet for exact links and content based on a detailed query."
    )
    args_schema: Type[BaseModel] = ExaSearchToolInput

    def _run(self, query: str) -> str:
        api_key = os.getenv("EXA_API_KEY")
        if not api_key:
            return "Error: EXA_API_KEY environment variable is missing."
        
        try:
            exa = Exa(api_key=api_key)
            result = exa.search_and_contents(
                query,
                type="auto",
                num_results=6,
                use_autoprompt=True,
                highlights=True
            )
            return str(result)
        except Exception as e:
            return f"Error executing Exa Search: {str(e)}"
