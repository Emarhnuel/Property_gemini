import os
import re
import json
from typing import List, Tuple, Any

from crewai import Agent, Crew, Process, Task, LLM
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task
from crewai.tasks.hallucination_guardrail import HallucinationGuardrail
from crewai.tasks.task_output import TaskOutput
from crewai_tools import TavilySearchTool, TavilyExtractorTool


OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


# ============== GUARDRAILS ==============

def truncate_listings_guardrail(result: TaskOutput) -> Tuple[bool, Any]:
    """
    Guardrail to ensure strictly no more than 6 listings are passed to the next step.
    If more than 6 are found, it truncates the list.
    """
    try:
        # Parse the result
        if isinstance(result.raw, str):
            # Clean up markdown code blocks if present
            clean_raw = result.raw.replace("```json", "").replace("```", "").strip()
            try:
                data = json.loads(clean_raw)
            except json.JSONDecodeError:
                return (False, "Output must be valid JSON to verify listing count.")
        else:
            data = result.raw

        # Check and Truncate
        if isinstance(data, dict) and "listings" in data and isinstance(data["listings"], list):
            count = len(data["listings"])
            if count > 6:
                # Slice the list to exactly 6
                data["listings"] = data["listings"][:6]
                
                # Update summary if present
                if "scrape_summary" in data:
                    data["scrape_summary"]["original_count"] = count
                    data["scrape_summary"]["truncated_count"] = 6
                    data["scrape_summary"]["note"] = "Listings truncated to 6 by guardrail."

        # Return success with the modified data
        # We dump it back to string to ensure consistency for the next task
        return (True, json.dumps(data))

    except Exception as e:
        return (False, f"Error in truncation guardrail: {str(e)}")


def validate_property_extraction(result: TaskOutput) -> Tuple[bool, Any]:
    """Validate that extracted property data contains all mandatory fields."""
    try:
        # Parse the result - handle both string and dict
        if isinstance(result.raw, str):
            clean_raw = result.raw.replace("```json", "").replace("```", "").strip()
            try:
                data = json.loads(clean_raw)
            except json.JSONDecodeError:
                return (False, "Output must be valid JSON")
        else:
            data = result.raw
        
        # Handle single property or list of properties
        properties = data if isinstance(data, list) else [data]
        
        mandatory_fields = [
            "phone_number",
            "property_url", 
            "property_location",
            "agent_name",  # or company_name
            "property_description",
            "image_url",
            "price"  # rent or purchase fee
        ]
        
        errors = []
        for i, prop in enumerate(properties):
            missing = []
            
            # Check phone number (with basic format validation)
            phone = prop.get("phone_number") or prop.get("contact", {}).get("phone")
            if not phone:
                missing.append("phone_number")
            elif phone and not re.match(r'^[\d\s\-\+\(\)]{7,}$', str(phone)):
                errors.append(f"Property {i+1}: Invalid phone format: {phone}")
            
            # Check property URL
            url = prop.get("property_url") or prop.get("listing_url") or prop.get("metadata", {}).get("listing_url")
            if not url:
                missing.append("property_url")
            elif url and not url.startswith(("http://", "https://")):
                errors.append(f"Property {i+1}: Invalid URL format: {url}")
            
            # Check location
            location = prop.get("property_location") or prop.get("location") or prop.get("details", {}).get("address")
            if not location:
                missing.append("property_location")
            
            # Check agent/company name
            agent_name = (prop.get("agent_name") or prop.get("company_name") or 
                         prop.get("contact", {}).get("name") or prop.get("contact", {}).get("brokerage"))
            if not agent_name:
                missing.append("agent_name or company_name")
            
            # Check description
            description = prop.get("property_description") or prop.get("description", {}).get("full_text")
            if not description:
                missing.append("property_description")
            
            # Check image URL
            image = prop.get("image_url") or prop.get("images")
            if not image:
                missing.append("image_url")
            
            # Check price
            price = prop.get("price") or prop.get("details", {}).get("price")
            if not price:
                missing.append("price")
            
            if missing:
                errors.append(f"Property {i+1} missing: {', '.join(missing)}")
        
        if errors:
            return (False, "Validation failed:\n" + "\n".join(errors))
        
        return (True, result.raw)
        
    except Exception as e:
        return (False, f"Validation error: {str(e)}")


# HallucinationGuardrail for validate_data task
hallucination_guardrail = HallucinationGuardrail(
    llm=LLM(model="openrouter/openai/gpt-4o-mini", base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY")),
    context="Property data extracted from real estate listing websites. All information must be directly from scraped content.",
    threshold=7.0  # Require 7+ faithfulness score
)

llm = LLM(
    model="openrouter/deepseek/deepseek-r1",
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    temperature=0.1,
    #stream=True
)


tavily_search = TavilySearchTool(
            search_depth="advanced",
            max_results=10,
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
            llm=llm,
            max_rpm=10,
            max_iter=10,
            cache=True, 
            respect_context_window=True, 
            max_retry_limit=3,
            tools=[tavily_search, tavily_extractor],
        )

    @agent
    def data_extractor(self) -> Agent:
        """Data extractor agent that structures property data."""
        return Agent(
            config=self.agents_config["data_extractor"],  # type: ignore[index]
            verbose=True,
            max_iter=6,
            llm=llm
        )

    @agent
    def validator(self) -> Agent:
        """Validator agent that ensures data quality."""
        return Agent(
            config=self.agents_config["validator"],  # type: ignore[index]
            verbose=True,
            max_iter=3,
            llm=llm 
        )

    @agent
    def report_agent(self) -> Agent:
        """Report agent that compiles results to JSON."""
        return Agent(
            config=self.agents_config["report_agent"],  # type: ignore[index]
            verbose=True,
            max_iter=5,
            llm=llm 
        )

    @task
    def scrape_listings(self) -> Task:
        """Task to scrape property listings from platforms."""
        return Task(
            config=self.tasks_config["scrape_listings"],  # type: ignore[index]
            guardrail=truncate_listings_guardrail, # Added the truncation guardrail here
            guardrail_max_retries=1, # No need to retry much, just truncate and proceed
        )

    @task
    def extract_property_data(self) -> Task:
        """Task to extract structured data from raw listings."""
        return Task(
            config=self.tasks_config["extract_property_data"],  # type: ignore[index]
            guardrail=validate_property_extraction,
            guardrail_max_retries=3,
        )

    @task
    def validate_data(self) -> Task:
        """Task to validate extracted property data."""
        return Task(
            config=self.tasks_config["validate_data"],  # type: ignore[index]
            guardrail=hallucination_guardrail,
            guardrail_max_retries=2,
        )


    @task
    def compile_research_report(self) -> Task:
        """Task to compile validated data into JSON report."""
        return Task(
            config=self.tasks_config["compile_research_report"],  # type: ignore[index]
            output_file="output/research_results.json",
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Research Crew with sequential process."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            memory=True,
            stream=True,
            planning=True,  
            verbose=True,
        )