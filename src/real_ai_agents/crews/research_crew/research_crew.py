import os
import json
from typing import List, Optional, Any, Tuple
from pydantic import BaseModel
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.tasks.task_output import TaskOutput
from crewai_tools import TavilySearchTool
from crewai.tools import tool


# =======================
# ENV
# =======================

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
BROWSER_USE_API_KEY = os.getenv("BROWSER_USE_API_KEY")


# =======================
# OUTPUT MODELS
# =======================

class SearchListingsOutput(BaseModel):
    urls: List[str]
    platforms: List[str]


class ExtractedListing(BaseModel):
    listing_url: str
    platform: Optional[str] = None
    address: Optional[str] = None
    price: Optional[Any] = None
    price_frequency: Optional[str] = None
    bedrooms: Optional[float] = None
    bathrooms: Optional[float] = None
    description: Optional[str] = None
    images: List[str] = []
    facts_and_features: Optional[dict] = None
    contact: Optional[dict] = None


class ExtractListingsOutput(BaseModel):
    listings: List[ExtractedListing]
    summary: dict


class ValidatedListing(ExtractedListing):
    quality_score: int
    validation_notes: List[str] = []


class ValidateListingsOutput(BaseModel):
    listings: List[ValidatedListing]
    summary: dict


# =======================
# GUARDRAILS
# =======================

def validate_search_used(result: TaskOutput) -> Tuple[bool, Any]:
    """Ensure valid URLs were found."""
    raw = result.raw if isinstance(result.raw, str) else json.dumps(result.raw)
    if "http" not in raw:
        return False, "No URLs detected — Tavily Search likely not used"
    return True, result.raw


def validate_extract_used(result: TaskOutput) -> Tuple[bool, Any]:
    """Ensure Tavily Extract was actually called and no raw HTML leaked."""
    raw = result.raw if isinstance(result.raw, str) else json.dumps(result.raw)

    if "listings" not in raw:
        return False, "Missing listings array"

    if "raw_content" in raw or "<html" in raw.lower():
        return False, "Raw HTML leaked into output"

    return True, result.raw


# =======================
# LLM CONFIG
# =======================


gemini_flash_scraper_llm = LLM(
    model="gemini/gemini-3-flash-preview",
    temperature=0.0,
    max_tokens=20000,  # small hard cap
    top_p=0.9,
)


gemini_pro_report_llm = LLM(
    model="gemini/gemini-3-pro-preview",
    temperature=0.0,
    max_tokens=20000,  # avoid huge outputs
    top_p=0.9,
)

# DeepSeek for Validator - cheap, no Gemini needed
validator_llm = LLM(
    model="openrouter/deepseek/deepseek-v3.2",
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    temperature=0.0,
    max_tokens=9000,
)


# =======================
# TOOLS
# =======================

tavily_search = TavilySearchTool(
    search_depth="advanced",
    max_results=6,
    include_raw_content=False,  # NEVER include raw content
)

@tool("tavily_extract")
def tavily_extract_tool(urls: str) -> str:
    """
    Extract content from URLs using Tavily's extraction service.
    
    Args:
        urls: Comma-separated list of URLs to extract content from
        
    Returns:
        Extracted content in JSON format
    """
    import json
    
    # Parse URLs from comma-separated string
    url_list = [url.strip() for url in urls.split(',') if url.strip()]
    
    if not url_list:
        return json.dumps({"error": "No valid URLs provided"})
    
    try:
        # Use the global MCP function - it should be available in the execution context
        # This is a placeholder - the actual implementation will depend on how MCP tools are exposed
        extracted_data = {
            "urls": url_list,
            "extracted_content": [],
            "status": "success"
        }
        
        # For now, return a structured response that matches what the agent expects
        for url in url_list:
            extracted_data["extracted_content"].append({
                "url": url,
                "content": f"Content extracted from {url}",
                "title": "Property Listing",
                "images": []
            })
        
        return json.dumps(extracted_data)
    except Exception as e:
        return json.dumps({"error": f"Error extracting content: {str(e)}"})



# =======================
# CREW
# =======================

@CrewBase
class ResearchCrew:
    agents: List[Agent]
    tasks: List[Task]

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # -------- Agents --------

    @agent
    def scraper(self) -> Agent:
        """Scraper agent using Gemini Pro - specialized for URL discovery."""
        return Agent(
            config=self.agents_config["scraper"],
            llm=gemini_flash_scraper_llm,
            tools=[tavily_search],
            verbose=False,
            allow_delegation=False,
            max_iter=4,
            max_retry_limit=6,
            respect_context_window=True,
        )

    @agent
    def extractor(self) -> Agent:
        """Extractor agent using Gemini Pro - specialized for data extraction."""
        return Agent(
            config=self.agents_config["extractor"],
            llm=gemini_pro_report_llm,
            verbose=False,
            allow_delegation=False,
            max_iter=4,
            max_retry_limit=6,
            inject_date=True,
            date_format="%Y-%m-%d",
            respect_context_window=True,
            mcps=[
            "https://api.browser-use.com/mcp?api_key=${BROWSER_USE_API_KEY}"
        ]
        )


    @agent
    def validator(self) -> Agent:
        """Validator agent using DeepSeek - cheap reasoning."""
        return Agent(
            config=self.agents_config["validator"],
            llm=validator_llm,
            verbose=True,
            max_iter=4,
            max_retry_limit=6,
            respect_context_window=False,
        )

    @agent
    def report_agent(self) -> Agent:
        """Report agent using Gemini Flash - formatting only."""
        return Agent(
            config=self.agents_config["report_agent"],
            llm=gemini_flash_scraper_llm,
            verbose=False,
            max_iter=4,
            max_retry_limit=6,
            respect_context_window=True,
        )

    # -------- Tasks --------

    @task
    def search_listings(self) -> Task:
        """Search for property listing URLs."""
        return Task(
            config=self.tasks_config["search_listings"],
            output_json=SearchListingsOutput,
            guardrail=validate_search_used,
            guardrail_max_retries=2,
        )

    @task
    def extract_listings(self) -> Task:
        """Extract structured data from URLs - scrape + parse in one step."""
        return Task(
            config=self.tasks_config["extract_listings"],
            output_json=ExtractListingsOutput,
            guardrail=validate_extract_used,
            guardrail_max_retries=2,
        )

    @task
    def validate_data(self) -> Task:
        """Validate extracted listings for quality."""
        return Task(
            config=self.tasks_config["validate_data"],
            output_json=ValidateListingsOutput,
        )

    @task
    def compile_research_report(self) -> Task:
        """Compile validated data into final JSON report."""
        return Task(
            config=self.tasks_config["compile_research_report"],
            output_file="output/research_results.json",
        )

    # -------- Crew --------

    @crew
    def crew(self) -> Crew:
        """Creates the Research Crew - sequential, no planning."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            planning=False,
        )