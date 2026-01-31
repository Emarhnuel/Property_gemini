import os
import json
from typing import List, Optional, Any, Tuple
from pydantic import BaseModel
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.tasks.task_output import TaskOutput
from crewai_tools import TavilySearchTool, TavilyExtractorTool


# =======================
# ENV
# =======================

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


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
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
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
    max_tokens=8000,  # small hard cap
    top_p=0.9,
)


gemini_pro_report_llm = LLM(
    model="gemini/gemini-3-pro-preview",
    temperature=0.0,
    max_tokens=8000,  # avoid huge outputs
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

tavily_extract = TavilyExtractorTool(
    extract_depth="advanced",
    include_images=True,
)


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
        """Scraper agent using Gemini Flash - single-shot, token-safe."""
        return Agent(
            config=self.agents_config["scraper"],
            llm=gemini_flash_scraper_llm,
            tools=[tavily_search, tavily_extract],
            verbose=False,              # logs cost tokens
            allow_delegation=False,
            max_iter=4,                 # single shot
            max_retry_limit=6,          # fail fast
            inject_date=True,
            date_format="%Y-%m-%d",
            respect_context_window=True,
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
            llm=gemini_pro_report_llm,
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