import os
import json
from typing import List, Optional, Any, Tuple
from pydantic import BaseModel
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.tasks.task_output import TaskOutput
from crewai_tools import TavilySearchTool
from real_ai_agents.tools.browser_use_tool import browser_extract_tool



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
    """
    Enforces:
    - Output is PURE JSON
    - No instruction echoing
    - No trailing characters
    - Required keys exist
    """
    raw = result.raw

    if not isinstance(raw, str):
        return False, "Output is not a string"

    raw = raw.strip()

    # Must start and end with JSON object
    if not raw.startswith("{") or not raw.endswith("}"):
        return False, "Output is not pure JSON (extra text detected)"

    try:
        data = json.loads(raw)
    except Exception as e:
        return False, f"Invalid JSON: {e}"

    # Required keys
    if set(data.keys()) != {"urls", "platforms"}:
        return False, "JSON must contain ONLY 'urls' and 'platforms' keys"

    # URLs validation
    if not isinstance(data["urls"], list) or len(data["urls"]) < 3:
        return False, "At least 3 URLs are required"

    if not all(isinstance(u, str) and u.startswith("http") for u in data["urls"]):
        return False, "All URLs must be valid http(s) strings"

    # Platform validation (zillow is blocked)
    blocked_platforms = {"zillow"}
    if any(p in blocked_platforms for p in data["platforms"]):
        return False, "Zillow is blocked - do not include zillow URLs"

    return True, data



def validate_extract_used(result: TaskOutput) -> Tuple[bool, Any]:
    """Ensure extraction output is valid and no raw HTML leaked"""
    raw = result.raw if isinstance(result.raw, str) else json.dumps(result.raw)

    if "listings" not in raw:
        return False, "Missing listings array"

    if "raw_content" in raw or "<html" in raw.lower():
        return False, "Raw HTML leaked into output"

    return True, result.raw



def browser_only_extraction_guardrail(result: TaskOutput) -> Tuple[bool, Any]:
    """
    Detects hallucinated (non-browser) extraction by enforcing
    browser-only output signals with realistic thresholds.
    """
    raw = result.raw if isinstance(result.raw, str) else json.dumps(result.raw)

    try:
        data = json.loads(raw)
    except Exception:
        return False, "Invalid JSON output"

    listings = data.get("listings", [])
    if not listings:
        return False, "No listings extracted"

    for listing in listings:
        images = listing.get("images", [])
        description = listing.get("description", "") or ""
        facts = listing.get("facts_and_features", {}) or {}

        # Realistic browser-only signals
        if len(images) < 2:
            return False, "Too few images — likely not browser-extracted"

        if len(description.split()) < 30:
            return False, "Description too short — likely hallucinated"

        if not isinstance(facts, dict) or len(facts.keys()) < 2:
            return False, "Insufficient facts/features — likely not browser data"

        # HTML leakage check
        if "<html" in description.lower():
            return False, "Raw HTML detected"

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

# OpenAI for Extractor - compatible with Browser Use MCP tool schemas
openai_extractor_llm = LLM(
    model="openai/gpt-5-mini-2025-08-07",
    temperature=0.0,
    max_tokens=16000,
)


# =======================
# TOOLS
# =======================

tavily_search = TavilySearchTool(
    search_depth="advanced",
    max_results=6,
    include_raw_content=False,  # NEVER include raw content
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
        """Extractor agent using Gemini Pro with Browser Use Cloud tool."""
        return Agent(
            config=self.agents_config["extractor"],
            llm=gemini_pro_report_llm,  # Gemini works with custom tool (no MCP schema issues)
            tools=[browser_extract_tool],  # Custom Browser Use Cloud tool
            verbose=False,
            allow_delegation=False,
            max_iter=4,
            max_retry_limit=6,
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
            guardrail=browser_only_extraction_guardrail,
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