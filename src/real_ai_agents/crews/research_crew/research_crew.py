import os
import re
import json
from typing import List, Tuple, Any, Optional
from pydantic import BaseModel


# ============== PYDANTIC OUTPUT MODELS ==============

class PropertyImage(BaseModel):
    url: Optional[str] = None
    caption: Optional[str] = None
    is_primary: Optional[bool] = None

class PropertyDetails(BaseModel):
    title: Optional[str] = None
    type: Optional[str] = None
    address: Optional[str] = None
    price: Optional[Any] = None  # Can be int, float, or string like "$2,500"
    price_frequency: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    sqft: Optional[int] = None
    year_built: Optional[int] = None
    lot_size: Optional[str] = None
    parking: Optional[str] = None
    furnished: Optional[str] = None
    pet_policy: Optional[str] = None
    available_date: Optional[str] = None
    lease_terms: Optional[str] = None

class PropertyFeatures(BaseModel):
    amenities: Optional[List[str]] = []
    utilities: Optional[List[str]] = []
    security: Optional[List[str]] = []
    appliances: Optional[List[str]] = []
    special: Optional[List[str]] = []

class PropertyDescription(BaseModel):
    full_text: Optional[str] = None
    neighborhood: Optional[str] = None

class PropertyContact(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    brokerage: Optional[str] = None
    photo_url: Optional[str] = None

class PropertyMetadata(BaseModel):
    listing_url: Optional[str] = None
    platform: Optional[str] = None
    listing_id: Optional[str] = None
    date_listed: Optional[str] = None
    days_on_market: Optional[int] = None
    status: Optional[str] = None

class PropertyRecord(BaseModel):
    images: Optional[List[PropertyImage]] = []
    details: Optional[PropertyDetails] = None
    features: Optional[PropertyFeatures] = None
    description: Optional[PropertyDescription] = None
    contact: Optional[PropertyContact] = None
    metadata: Optional[PropertyMetadata] = None
    extraction_notes: Optional[str] = None

class PropertyListOutput(BaseModel):
    """Output model for extract_property_data task."""
    listings: List[PropertyRecord]


# ============== REPORT OUTPUT MODEL ==============

class PropertySpecs(BaseModel):
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    sqft: Optional[int] = None
    type: Optional[str] = None

class ReportContact(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    company: Optional[str] = None

class ReportProperty(BaseModel):
    id: str
    display_title: Optional[str] = None
    price_display: Optional[str] = None
    location_display: Optional[str] = None
    primary_image: Optional[str] = None
    all_images: Optional[List[str]] = []
    specs: Optional[PropertySpecs] = None
    contact: Optional[ReportContact] = None
    listing_url: Optional[str] = None

class ReportMetadata(BaseModel):
    search_criteria: Optional[str] = None
    generated_at: Optional[str] = None
    total_found: Optional[int] = None
    total_validated: Optional[int] = None

class ReportIssues(BaseModel):
    properties_with_no_contact: Optional[List[str]] = []
    properties_with_no_images: Optional[List[str]] = []
    properties_flagged: Optional[List[str]] = []

class ResearchReportOutput(BaseModel):
    """Output model for compile_research_report task."""
    metadata: Optional[ReportMetadata] = None
    properties: List[ReportProperty]
    issues: Optional[ReportIssues] = None

from crewai import Agent, Crew, Process, Task, LLM
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task
from crewai.tasks.hallucination_guardrail import HallucinationGuardrail
from crewai.tasks.task_output import TaskOutput
from crewai_tools import TavilySearchTool, TavilyExtractorTool


OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


# ============== GUARDRAILS ==============


# def validate_property_extraction(result: TaskOutput) -> Tuple[bool, Any]:
#     """Validate that extracted property data contains mandatory field keywords."""
#     try:
#         raw_output = result.raw if isinstance(result.raw, str) else str(result.raw)
        
#         # Check for mandatory fields with ACTUAL content (not null, not empty)
#         mandatory_patterns = [
#             # phone_number: must have digits (7+ chars like +1-555-123-4567)
#             (r'"phone":\s*"[\d\s\-\+\(\)]{7,}"|"phone_number":\s*"[\d\s\-\+\(\)]{7,}"', "phone_number (must have 7+ digit phone)"),
#             # property_url: must be http:// or https:// URL
#             (r'"listing_url":\s*"https?://[^"]+"|"property_url":\s*"https?://[^"]+"', "property_url (must be valid URL)"),
#             # property_location: must have actual text (at least 5 chars)
#             (r'"address":\s*"[^"]{5,}"|"property_location":\s*"[^"]{5,}"', "property_location (must have address text)"),
#             # agent_name/company: must have actual name (at least 2 chars)
#             (r'"name":\s*"[^"]{2,}"|"agent_name":\s*"[^"]{2,}"|"brokerage":\s*"[^"]{2,}"|"company_name":\s*"[^"]{2,}"', "agent_name/company_name (must have name)"),
#             # description: must have actual text (at least 10 chars)
#             (r'"full_text":\s*"[^"]{10,}"|"property_description":\s*"[^"]{10,}"', "property_description (must have description text)"),
#             # image_url: must have actual http URL inside array or field
#             (r'"images":\s*\[\s*\{[^}]*"url":\s*"https?://|"image_url":\s*"https?://[^"]+"|"primary_image":\s*"https?://[^"]+"', "image_url (must have image URL)"),
#             # price: must have actual number (digits)
#             (r'"price":\s*\d+|"price":\s*"\$?[\d,]+"', "price (must have numeric price)"),
#         ]
        
#         missing = []
#         for pattern, field_name in mandatory_patterns:
#             if not re.search(pattern, raw_output, re.IGNORECASE):
#                 missing.append(field_name)
        
#         if missing:
#             return (False, f"Missing mandatory fields: {', '.join(missing)}")
        
#         # Parse JSON and return dict (required when using output_json=PydanticModel)
#         clean_output = raw_output.replace("```json", "").replace("```", "").strip()
#         parsed_data = json.loads(clean_output)
#         return (True, parsed_data)
        
#     except json.JSONDecodeError as e:
#         return (False, f"Invalid JSON format: {str(e)}")
#     except Exception as e:
#         return (False, f"Validation error: {str(e)}")


# HallucinationGuardrail for validate_data task
hallucination_guardrail = HallucinationGuardrail(
    llm=LLM(model="openrouter/openai/gpt-4o-mini", base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY")),
    context="Property data extracted from real estate listing websites. All information must be directly from scraped content.",
    threshold=7.0  # Require 7+ faithfulness score
)

llm = LLM(
    model="openrouter/x-ai/grok-4.1-fast",
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    temperature=0.1,
    #stream=True
)

llm1 = LLM(
    model="openrouter/google/gemini-3-flash-preview",
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    temperature=0.1,
    #stream=True
)
 

gemini_llm = LLM(
    model="gemini/gemini-3-flash-preview",
    temperature=0.3,
)


tavily_search = TavilySearchTool(
            search_depth="advanced",
            max_results=4,
            include_raw_content=True,
            include_images=True
        )
        
tavily_extractor = TavilyExtractorTool(
            extract_depth="advanced",
            include_images=True
        )

@CrewBase
class ResearchCrew:
    """Research Agent Crew - Sequential process for property discovery.
    
    This crew handles the Deep Discovery phase:
    1. Scraper - Finds listings on real estate platforms
    2. Data Extractor - Structures property data
    3. Validator - Ensures data quality
    4. Report Agent - Compiles JSON for Human Decision Gate
    
    Process: Sequential - Each step depends on the previous output.
    """

    agents: List[BaseAgent]
    tasks: List[Task]

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def scraper(self) -> Agent:
        """Scraper agent that finds property listings."""        
        return Agent(
            config=self.agents_config["scraper"],  # type: ignore[index]
            verbose=True,
            llm=llm1,
            max_iter=10,
            # cache=True,
            respect_context_window=True, 
            max_retry_limit=6,
            max_execution_time=200,
            inject_date=True,
            date_format="%Y-%m-%d",
            tools=[tavily_search, tavily_extractor],
        )
 
    @agent
    def data_extractor(self) -> Agent:
        """Data extractor agent that structures property data."""
        return Agent(
            config=self.agents_config["data_extractor"],  # type: ignore[index]
            verbose=True,
            max_iter=7,
            max_retry_limit=6,
            max_execution_time=120,
            respect_context_window=True,
            llm=llm
        )

    @agent
    def validator(self) -> Agent:
        """Validator agent that ensures data quality."""
        return Agent(
            config=self.agents_config["validator"],  # type: ignore[index]
            verbose=True,
            max_iter=3,
            max_retry_limit=3,
            max_execution_time=100,
            llm=llm 
        )

    @agent
    def report_agent(self) -> Agent:
        """Report agent that compiles results to JSON."""
        return Agent(
            config=self.agents_config["report_agent"],  # type: ignore[index]
            verbose=True,
            max_iter=5,
            respect_context_window=True,
            max_retry_limit=3,
            max_execution_time=120,
            llm=llm1
        )

    @task
    def scrape_listings(self) -> Task:
        """Task to scrape property listings from platforms."""
        return Task(
            config=self.tasks_config["scrape_listings"],  # type: ignore[index]
        )

    @task
    def extract_property_data(self) -> Task:
        """Task to extract structured data from raw listings."""
        return Task(
            config=self.tasks_config["extract_property_data"],  # type: ignore[index]
            #guardrail=validate_property_extraction,
            #guardrail_max_retries=3,
            output_json=PropertyListOutput,
        )

    @task
    def validate_data(self) -> Task:
        """Task to validate extracted property data."""
        return Task(
            config=self.tasks_config["validate_data"],  # type: ignore[index]
            # guardrail=hallucination_guardrail,
            # guardrail_max_retries=2,
        )


    @task
    def compile_research_report(self) -> Task:
        """Task to compile validated data into JSON report."""
        return Task(
            config=self.tasks_config["compile_research_report"],  # type: ignore[index]
            output_file="output/research_results.json",
            output_json=ResearchReportOutput,
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Research Crew with sequential process."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            memory=False,
            stream=False,
            planning=True,  
            verbose=True,
        )